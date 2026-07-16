import os
import math
import threading
import time
from typing import Dict, Tuple, List

import cv2
import networkx as nx
from flask import Flask, jsonify, request
from flask_cors import CORS

# ------------------------------
# Config
# ------------------------------
VIDEO_PATH = os.path.join('slow.mp4')
FRAME_SKIP = 2           # process every Nth frame for efficiency
SMOOTHING = 0.6          # EMA smoothing factor for flow
REFRESH_SECONDS = 2      # API update frequency (match traffic_project_hybrid)

ALPHA_LENGTH = 0.3       # weight factor for road length cost
BETA_FLOW = 1.0          # weight factor for dynamic flow cost

# ------------------------------
# Global state guarded by lock
# ------------------------------
_state_lock = threading.Lock()
# Per-edge dynamic flow (vehicles) estimated from video frames
_edge_flow: Dict[Tuple[str, str], float] = {}
_edge_ema: Dict[Tuple[str, str], float] = {}
_edge_last_count: Dict[Tuple[str, str], int] = {}

# The city graph (30 junctions)
G = nx.Graph()
NODE_POS: Dict[str, Tuple[int, int]] = {}

# ------------------------------
# Utilities
# ------------------------------

def edge_key(a: str, b: str) -> Tuple[str, str]:
    return (a, b) if a <= b else (b, a)


# ------------------------------
# Build a city-like 6x5 grid (cols x rows = 30 nodes),
# add arterials (long diagonals), and unequal road lengths.
# ------------------------------

def build_city_graph():
    cols, rows = 6, 5  # 6 columns, 5 rows = 30 nodes
    spacing_x, spacing_y = 220, 180

    # Create nodes with positions (x,y) for frontend placement
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c + 1
            nid = f"J{idx}"
            # Stagger some rows slightly for a city-like irregular feel
            jitter_x = (r % 2) * 40
            jitter_y = (c % 2) * 20
            x = c * spacing_x + jitter_x
            y = r * spacing_y + jitter_y
            G.add_node(nid)
            NODE_POS[nid] = (x, y)

    # Helper to compute Euclidean length between nodes
    def length(a: str, b: str) -> float:
        (x1, y1), (x2, y2) = NODE_POS[a], NODE_POS[b]
        return math.hypot(x2 - x1, y2 - y1) / 100.0  # scaled to ~road km units

    # Grid connections (horizontal and vertical)
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c + 1
            nid = f"J{idx}"
            # connect right neighbor
            if c < cols - 1:
                right = f"J{idx + 1}"
                G.add_edge(nid, right, length=length(nid, right))
            # connect down neighbor
            if r < rows - 1:
                down = f"J{idx + cols}"
                G.add_edge(nid, down, length=length(nid, down))

    # Add a few diagonals / ring roads (arterials)
    arterials = [
        ('J1', 'J7'), ('J2', 'J8'), ('J3', 'J9'), ('J4', 'J10'),
        ('J5', 'J11'), ('J6', 'J12'),  # vertical arterials spanning two rows
        ('J7', 'J19'), ('J12', 'J24'), # long vertical jumps
        ('J1', 'J12'), ('J6', 'J17'),  # diagonals across grid
        ('J10', 'J21'), ('J15', 'J26'),
        ('J5', 'J18'), ('J13', 'J30'),
    ]
    for a, b in arterials:
        if a in G and b in G:
            G.add_edge(a, b, length=length(a, b))

    # Initialize dynamic attrs (flow will be filled by video worker)
    for u, v in G.edges():
        L = G[u][v]['length']
        _edge_flow[edge_key(u, v)] = 5.0  # initial guess
        _edge_ema[edge_key(u, v)] = 5.0
        _edge_last_count[edge_key(u, v)] = 0
        G[u][v]['weight'] = ALPHA_LENGTH * L + BETA_FLOW * _edge_flow[edge_key(u, v)]


class VideoSegment:
    """Independent reader for a shared video file with a custom frame interval."""
    def __init__(self, video_path: str, frame_interval: int):
        self.video_path = video_path
        self.frame_interval = max(1, int(frame_interval))
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print(f"[WARN] Could not open video: {video_path}")
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        self.current_frame = 0

    def get_next_frame(self):
        if not self.cap.isOpened():
            return None
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        if not ret:
            # loop
            self.current_frame = 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                return None
        self.current_frame = (self.current_frame + self.frame_interval) % self.total_frames
        return frame

    def close(self):
        try:
            self.cap.release()
        except Exception:
            pass


def count_vehicles_from_frame(frame) -> int:
    """Count vehicles from a frame using edge detection"""
    if frame is None:
        return 0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blur, 80, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    vehicles = [cnt for cnt in contours if cv2.contourArea(cnt) > 400]
    return len(vehicles)


# ------------------------------
# Periodic graph weight updater based on current flow
# ------------------------------

def edges_video_update_worker(segments: Dict[Tuple[str, str], VideoSegment]):
    """Update per-edge vehicle flow by reading frames with per-edge intervals."""
    # initialize EMAs
    for k in segments.keys():
        _edge_ema.setdefault(k, 5.0)
        _edge_flow.setdefault(k, 5.0)

    while True:
        for k, seg in segments.items():
            frame = seg.get_next_frame()
            count = count_vehicles_from_frame(frame)
            # EMA smoothing
            prev = _edge_ema.get(k, 5.0)
            ema = SMOOTHING * prev + (1.0 - SMOOTHING) * count
            with _state_lock:
                _edge_ema[k] = ema
                _edge_flow[k] = max(0.0, float(ema))
                _edge_last_count[k] = int(count)
        time.sleep(REFRESH_SECONDS)


def graph_update_worker():
    while True:
        # Update each edge with combined cost: length + per-edge dynamic flow
        for u, v, d in G.edges(data=True):
            L = d.get('length', 1.0)
            flow = _edge_flow.get(edge_key(u, v), 5.0)
            d['weight'] = ALPHA_LENGTH * L + BETA_FLOW * flow
        time.sleep(REFRESH_SECONDS)


# ------------------------------
# Flask API
# ------------------------------
app = Flask(__name__)
CORS(app)

@app.route('/api/graph_data')
def api_graph_data():
    # Read optional source/target from query
    src = request.args.get('src', 'J1')
    dst = request.args.get('dst', 'J30')
    # Compute min/max for frontend normalization
    weights: List[float] = [d['weight'] for _, _, d in G.edges(data=True)]
    min_w = min(weights) if weights else 0.0
    max_w = max(weights) if weights else 1.0

    # Build nodes with positions for frontend
    nodes = [{
        'id': n,
        'label': n,
        'x': NODE_POS[n][0],
        'y': NODE_POS[n][1]
    } for n in G.nodes()]

    edges = []
    for u, v, d in G.edges(data=True):
        k = edge_key(u, v)
        edges.append({
            'from': u,
            'to': v,
            'weight': float(d['weight']),
            'count': int(_edge_last_count.get(k, 0)),
            'label': str(int(_edge_last_count.get(k, 0)))
        })

    # Compute best route between requested src and dst
    try:
        if src not in G or dst not in G:
            raise nx.NodeNotFound("invalid src/dst")
        best_route = nx.shortest_path(G, source=src, target=dst, weight='weight')
    except Exception:
        best_route = []

    return jsonify({
        'nodes': nodes,
        'edges': edges,
        'best_route': best_route,
        'min_weight': float(min_w),
        'max_weight': float(max_w),
        'src': src,
        'dst': dst,
        'next_update': REFRESH_SECONDS
    })


# ------------------------------
# Entry point
# ------------------------------
if __name__ == '__main__':
    build_city_graph()

    # Create a per-edge video segment with different frame intervals
    intervals = [5, 8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 35,37,39,41,43,45,47,49]
    segments: Dict[Tuple[str, str], VideoSegment] = {}
    for i, (u, v) in enumerate(G.edges()):
        k = edge_key(u, v)
        if k in segments:
            continue
        interval = intervals[i % len(intervals)]
        segments[k] = VideoSegment(VIDEO_PATH, frame_interval=interval)

    # Start workers
    threading.Thread(target=edges_video_update_worker, args=(segments,), daemon=True).start()
    threading.Thread(target=graph_update_worker, daemon=True).start()

    print('Hybrid backend running at http://127.0.0.1:5000')
    print('Endpoint: GET /api/graph_data')
    app.run(host='127.0.0.1', port=5000, debug=True)
