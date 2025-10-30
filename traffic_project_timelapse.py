"""
Traffic Management System with Time-lapse Video Support
This version uses time-lapse videos instead of static images
"""
import os
import networkx as nx
from flask import Flask, jsonify, send_file
from flask_cors import CORS
import time
from timelapse_traffic import TimelapseTrafficAnalyzer

# Initialize time-lapse analyzer
timelapse_analyzer = TimelapseTrafficAnalyzer(video_folder='videos', frame_interval=30)

# Map segments to time-lapse video files
# Place your time-lapse videos in the 'videos/' folder
video_mapping = {
    'Start_R1': 'videos/start_r1_timelapse.mp4',
    'R1_R2': 'videos/r1_r2_timelapse.mp4',
    'R2_R3': 'videos/r2_r3_timelapse.mp4',
    'R3_R4': 'videos/r3_r4_timelapse.mp4',
    'R4_End': 'videos/r4_end_timelapse.mp4',
    'U1_R1': 'videos/u1_r1_timelapse.mp4',
    'U1_R2': 'videos/u1_r2_timelapse.mp4',
    'U2_R3': 'videos/u2_r3_timelapse.mp4',
    'U2_R4': 'videos/u2_r4_timelapse.mp4',
    'L1_R1': 'videos/l1_r1_timelapse.mp4',
    'L1_R2': 'videos/l1_r2_timelapse.mp4',
    'L2_R3': 'videos/l2_r3_timelapse.mp4',
    'L2_R4': 'videos/l2_r4_timelapse.mp4',
    'L1_L2': 'videos/l1_l2_timelapse.mp4',
    'U1_U2': 'videos/u1_u2_timelapse.mp4',
}

# Load videos
print("Initializing Traffic Management System with Time-lapse Videos...")
timelapse_analyzer.load_videos(video_mapping)

# Initialize traffic data
road_density = {}
last_update_time = time.time()

def update_traffic_from_videos():
    """Update traffic counts from time-lapse video frames"""
    global road_density, last_update_time
    
    print(f"\nUpdating traffic from video frames at {time.strftime('%H:%M:%S')}...")
    counts = timelapse_analyzer.get_all_traffic_counts()
    
    for segment, count in counts.items():
        road_density[segment] = count
        print(f"  {segment}: {count} vehicles")
    
    last_update_time = time.time()
    return road_density

# Initial update
update_traffic_from_videos()

# Build the traffic graph
nodes = ['Start', 'R1', 'R2', 'R3', 'R4', 'End', 'U1', 'U2', 'L1', 'L2']

# Calculate best route
def get_current_best_route():
    """Calculate the best route based on current traffic"""
    G = nx.Graph()
    G.add_nodes_from(nodes)
    
    edges = [
        ('Start', 'R1', road_density.get('Start_R1', 0)),
        ('R1', 'R2', road_density.get('R1_R2', 0)),
        ('R2', 'R3', road_density.get('R2_R3', 0)),
        ('R3', 'R4', road_density.get('R3_R4', 0)),
        ('R4', 'End', road_density.get('R4_End', 0)),
        ('U1', 'R1', road_density.get('U1_R1', 0)),
        ('U1', 'R2', road_density.get('U1_R2', 0)),
        ('U2', 'R3', road_density.get('U2_R3', 0)),
        ('U2', 'R4', road_density.get('U2_R4', 0)),
        ('L1', 'R1', road_density.get('L1_R1', 0)),
        ('L1', 'R2', road_density.get('L1_R2', 0)),
        ('L2', 'R3', road_density.get('L2_R3', 0)),
        ('L2', 'R4', road_density.get('L2_R4', 0)),
        ('L1', 'L2', road_density.get('L1_L2', 0)),
        ('U1', 'U2', road_density.get('U1_U2', 0)),
    ]
    
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    
    try:
        best_route = nx.shortest_path(G, source='Start', target='End', weight='weight')
        print(f"Best route: {' -> '.join(best_route)}")
        return best_route, G
    except:
        return ['Start', 'R1', 'R2', 'R3', 'R4', 'End'], G

initial_route, _ = get_current_best_route()

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
    
    # Update from video every 5 seconds for smoother updates
    if current_time - last_update_time >= 5:
        update_traffic_from_videos()
    
    # Get current best route and graph
    current_best_route, G_current = get_current_best_route()
    
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
        'next_update': int(5 - (current_time - last_update_time))
    })

if __name__ == "__main__":
    print("Starting Flask server at http://127.0.0.1:5000")
    print("Traffic data updates from time-lapse videos every 5 seconds")
    try:
        app.run(debug=True)
    finally:
        timelapse_analyzer.close()
