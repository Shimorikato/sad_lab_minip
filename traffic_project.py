import os
import cv2
import networkx as nx
from flask import Flask, jsonify, send_file
from flask_cors import CORS
from pyvis.network import Network
import random
import time

# Function to count vehicles in an image file
def count_vehicles(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Warning: Image file {image_path} not found or unreadable.")
        return 0
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blur, 80, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    vehicles = [cnt for cnt in contours if cv2.contourArea(cnt) > 400]
    return len(vehicles)

# Define road images for your network
road_images = {
    'Start_R1': 'images/Start_r1.png',
    'R1_R2': 'images/r1_r2.png',
    'R2_R3': 'images/r2_r3.png',
    'R3_R4': 'images/r3_r4.png',
    'R4_End': 'images/r4_end.png',
    'U1_R1': 'images/u1_r1.png',
    'U1_R2': 'images/u1_r2.png',
    'U2_R3': 'images/u2_r3.png',
    'U2_R4': 'images/u2_r4.png',
    'L1_R1': 'images/l1_r1.png',
    'L1_R2': 'images/l1_r2.png',
    'L2_R3': 'images/l2_r3.png',
    'L2_R4': 'images/l2_r4.png',
    'L1_L2': 'images/l1-l2.jpg',
    'U1_U2': 'images/u1_u2.png',
}


# Count vehicles on each road segment
road_density = {}
for edge, path in road_images.items():
    road_density[edge] = count_vehicles(path)
    print(f"Vehicle count on {edge}: {road_density[edge]}")

# Build the traffic graph
G = nx.Graph()

nodes = ['Start', 'R1', 'R2', 'R3', 'R4', 'End', 'U1', 'U2', 'L1', 'L2']
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

# Calculate best route example
best_route = nx.shortest_path(G, source='Start', target='End', weight='weight')
print("Best route (least congested):", ' -> '.join(best_route))

# Flask app to serve graph and data
app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS for React frontend

@app.route('/')
def home():
    return send_file('templates/graph.html')

@app.route('/api/graph_data')
def graph_data():
    # Calculate min/max for normalization
    weights = [d['weight'] for u, v, d in G.edges(data=True)]
    min_weight = min(weights) if weights else 0
    max_weight = max(weights) if weights else 1
    
    nodes_list = [{'id': n, 'label': n} for n in G.nodes()]
    edges_list = [{
        'from': u, 
        'to': v, 
        'weight': d['weight'],
        'label': str(d['weight'])
    } for u, v, d in G.edges(data=True)]
    
    return jsonify({
        'nodes': nodes_list, 
        'edges': edges_list, 
        'best_route': best_route,
        'min_weight': min_weight,
        'max_weight': max_weight,
        'timestamp': time.time()
    })

if __name__ == "__main__":
    print("Starting Flask server at http://127.0.0.1:5000")
    app.run(debug=True)
