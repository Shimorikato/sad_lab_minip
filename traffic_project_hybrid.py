"""
Hybrid Traffic Management System
Uses time-lapse video for one road segment and static images for others
"""
import os
import cv2
import networkx as nx
from flask import Flask, jsonify, send_file
from flask_cors import CORS
import time

# Simple video frame extractor for one segment
class VideoSegment:
    def __init__(self, video_path, frame_interval=30):
        self.video_path = video_path
        self.frame_interval = frame_interval
        self.cap = cv2.VideoCapture(video_path)
        self.current_frame = 0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Loaded video: {video_path} ({self.total_frames} frames)")
        
    def get_next_frame(self):
        """Get next frame from video"""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        
        if ret:
            self.current_frame += self.frame_interval
            if self.current_frame >= self.total_frames:
                self.current_frame = 0
                print("  Video looped back to start")
            return frame
        else:
            self.current_frame = 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return None
            
    def close(self):
        self.cap.release()

# Function to count vehicles
def count_vehicles(image_or_frame):
    """Count vehicles from image path or frame"""
    if isinstance(image_or_frame, str):
        # It's a file path
        img = cv2.imread(image_or_frame)
        if img is None:
            print(f"Warning: Image file {image_or_frame} not found or unreadable.")
            return 0
    else:
        # It's a frame
        img = image_or_frame
        if img is None:
            return 0
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blur, 80, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    vehicles = [cnt for cnt in contours if cv2.contourArea(cnt) > 400]
    return len(vehicles)

# Initialize video segments for all roads
video_segments = {
    'Start_R1': VideoSegment('slow.mp4', frame_interval=15),
    'R1_R2': VideoSegment('slow.mp4', frame_interval=25),
    'R2_R3': VideoSegment('slow.mp4', frame_interval=5),
    'R3_R4': VideoSegment('slow.mp4', frame_interval=35),
    'R4_End': VideoSegment('slow.mp4', frame_interval=10),
    'U1_R1': VideoSegment('slow.mp4', frame_interval=11),
    'U1_R2': VideoSegment('slow.mp4', frame_interval=12),
    'U2_R3': VideoSegment('slow.mp4', frame_interval=13),
    'U2_R4': VideoSegment('slow.mp4', frame_interval=14),
    'L1_R1': VideoSegment('slow.mp4', frame_interval=15),
    'L1_R2': VideoSegment('slow.mp4', frame_interval=16),
    'L2_R3': VideoSegment('slow.mp4', frame_interval=17),
    'L2_R4': VideoSegment('slow.mp4', frame_interval=18),
    'L1_L2': VideoSegment('slow.mp4', frame_interval=19),
    'U1_U2': VideoSegment('slow.mp4', frame_interval=20),
}

# Initial count for all video segments
print("Analyzing video segments...")
road_density = {}
for edge, video_seg in video_segments.items():
    frame = video_seg.get_next_frame()
    road_density[edge] = count_vehicles(frame)
    print(f"  {edge} (video): {road_density[edge]} vehicles")

last_update_time = time.time()

def update_video_segments():
    """Update traffic counts from all video frames"""
    global last_update_time
    for edge, video_seg in video_segments.items():
        frame = video_seg.get_next_frame()
        count = count_vehicles(frame)
        road_density[edge] = count
    last_update_time = time.time()
    print(f"Updated all segments from videos")
    return True

# Build the traffic graph
nodes = ['Start', 'R1', 'R2', 'R3', 'R4', 'End', 'U1', 'U2', 'L1', 'L2']

def get_current_graph_and_route():
    """Get current graph and best route"""
    G = nx.Graph()
    G.add_nodes_from(nodes)
    
    edges = [
        ('Start', 'R1', road_density['Start_R1']),
        ('R1', 'R2', road_density['R1_R2']),
        ('R2', 'R3', road_density['R2_R3']),
        ('R3', 'R4', road_density['R3_R4']),
        ('R4', 'End', road_density['R4_End']),
        ('U1', 'R1', road_density['U1_R1']),
        ('U1', 'R2', road_density['U1_R2']),
        ('U2', 'R3', road_density['U2_R3']),
        ('U2', 'R4', road_density['U2_R4']),
        ('L1', 'R1', road_density['L1_R1']),
        ('L1', 'R2', road_density['L1_R2']),
        ('L2', 'R3', road_density['L2_R3']),
        ('L2', 'R4', road_density['L2_R4']),
        ('L1', 'L2', road_density['L1_L2']),
        ('U1', 'U2', road_density['U1_U2']),
    ]
    
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    
    try:
        best_route = nx.shortest_path(G, source='Start', target='End', weight='weight')
    except:
        best_route = ['Start', 'R1', 'R2', 'R3', 'R4', 'End']
    
    return G, best_route

G, best_route = get_current_graph_and_route()
print(f"Best route: {' -> '.join(best_route)}")

# Flask app
app = Flask(__name__, template_folder='templates')
CORS(app)

@app.route('/')
def home():
    return send_file('templates/graph.html')

@app.route('/api/graph_data')
def graph_data():
    global last_update_time
    
    current_time = time.time()
    
    # Update video segments every 2 seconds
    if current_time - last_update_time >= 2:
        update_video_segments()
    
    # Get current graph and route
    G_current, current_best_route = get_current_graph_and_route()
    
    # Calculate min/max for normalization
    weights = [d['weight'] for u, v, d in G_current.edges(data=True)]
    min_weight = min(weights) if weights else 0
    max_weight = max(weights) if weights else 1
    
    nodes_list = [{'id': n, 'label': n} for n in G_current.nodes()]
    edges_list = [{
        'from': u,
        'to': v,
        'weight': d['weight'],
        'label': str(d['weight'])
    } for u, v, d in G_current.edges(data=True)]
    
    return jsonify({
        'nodes': nodes_list,
        'edges': edges_list,
        'best_route': current_best_route,
        'min_weight': min_weight,
        'max_weight': max_weight,
        'timestamp': current_time,
        'next_update': int(2 - (current_time - last_update_time))
    })

if __name__ == "__main__":
    print("\nStarting Hybrid Traffic Management System")
    print("- All segments: Update from videos every 2 seconds")
    print(f"Server: http://127.0.0.1:5000\n")
    
    try:
        app.run(debug=True)
    finally:
        for edge, video_seg in video_segments.items():
            video_seg.close()
        print("All video segments closed")
