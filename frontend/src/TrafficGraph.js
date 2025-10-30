import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network/standalone';
import './TrafficGraph.css';

const TrafficGraph = () => {
  const containerRef = useRef(null);
  const networkRef = useRef(null);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [nextUpdate, setNextUpdate] = useState(60);

  // Fetch graph data from Flask backend
  const fetchGraphData = async () => {
    try {
      const response = await fetch('/api/graph_data');
      if (!response.ok) {
        throw new Error('Failed to fetch graph data');
      }
      const data = await response.json();
      setGraphData(data);
      setLastUpdate(new Date().toLocaleTimeString());
      setNextUpdate(data.next_update || 60);
      setLoading(false);
      setError(null);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphData();
    // Refresh every 1 second to show traffic movement
    const interval = setInterval(fetchGraphData, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!graphData || !containerRef.current) return;

    // Color interpolation function (blue for low, red for high)
    const getColorForWeight = (weight, minWeight, maxWeight) => {
      if (maxWeight === minWeight) return '#4299e1'; // Default blue if all same
      
      const normalized = (weight - minWeight) / (maxWeight - minWeight);
      
      // Interpolate from blue (low traffic) to red (high traffic)
      const r = Math.round(66 + normalized * (239 - 66));
      const g = Math.round(153 + normalized * (68 - 153));
      const b = Math.round(225 + normalized * (68 - 225));
      
      return `rgb(${r}, ${g}, ${b})`;
    };

    const { nodes, edges, best_route, min_weight, max_weight } = graphData;

    // Create nodes with custom styling and fixed positions
    const nodePositions = {
      'Start': { x: 0, y: 0 },
      'R1': { x: 250, y: 0 },
      'R2': { x: 500, y: 0 },
      'R3': { x: 750, y: 0 },
      'R4': { x: 1000, y: 0 },
      'End': { x: 1250, y: 0 },
      'U1': { x: 500, y: -200 },
      'U2': { x: 750, y: -200 },
      'L1': { x: 500, y: 200 },
      'L2': { x: 750, y: 200 }
    };

    const nodesDataset = nodes.map(node => ({
      id: node.id,
      label: node.label,
      shape: 'dot',
      size: 15,
      x: nodePositions[node.id]?.x || 0,
      y: nodePositions[node.id]?.y || 0,
      fixed: { x: true, y: true },
      color: {
        background: '#667eea',
        border: '#764ba2',
        highlight: {
          background: '#f59e0b',
          border: '#d97706'
        }
      },
      font: {
        color: '#1a202c',
        size: 16,
        face: 'Arial',
        bold: true
      }
    }));

    // Create edges with color based on traffic density
    const edgesDataset = edges.map(edge => {
      const isOnBestRoute = best_route && (
        (best_route.indexOf(edge.from) >= 0 && 
         best_route.indexOf(edge.to) === best_route.indexOf(edge.from) + 1) ||
        (best_route.indexOf(edge.to) >= 0 && 
         best_route.indexOf(edge.from) === best_route.indexOf(edge.to) + 1)
      );

      const edgeColor = getColorForWeight(edge.weight, min_weight, max_weight);

      return {
        from: edge.from,
        to: edge.to,
        label: `${edge.weight} vehicles`,
        color: {
          color: isOnBestRoute ? '#10b981' : edgeColor,
          highlight: '#f59e0b',
          opacity: 0.8
        },
        width: isOnBestRoute ? 5 : 3,
        smooth: {
          type: 'continuous',
          roundness: 0.5
        },
        font: {
          color: '#1a202c',
          size: 12,
          background: 'white',
          strokeWidth: 0
        },
        arrows: {
          to: {
            enabled: false
          }
        }
      };
    });

    const data = {
      nodes: nodesDataset,
      edges: edgesDataset
    };

    const options = {
      physics: {
        enabled: false
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
        zoomView: true,
        dragView: true
      },
      layout: {
        hierarchical: false
      },
      edges: {
        smooth: {
          type: 'continuous',
          roundness: 0.2
        }
      }
    };

    // Create or update network
    if (networkRef.current) {
      // Only update the data, preserve zoom and position
      const currentPosition = networkRef.current.getViewPosition();
      const currentScale = networkRef.current.getScale();
      networkRef.current.setData(data);
      networkRef.current.moveTo({
        position: currentPosition,
        scale: currentScale,
        animation: false
      });
    } else {
      networkRef.current = new Network(containerRef.current, data, options);
    }

  }, [graphData]);

  if (loading) {
    return (
      <div className="traffic-graph-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading traffic data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="traffic-graph-container">
        <div className="error">
          <h3>⚠️ Error Loading Data</h3>
          <p>{error}</p>
          <button onClick={fetchGraphData} className="retry-btn">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="traffic-graph-container">
      <div className="info-panel">
        <div className="info-card">
          <h3>Best Route (Least Congested)</h3>
          <div className="route-path">
            {graphData?.best_route?.join(' → ')}
          </div>
        </div>
        <div className="info-card">
          <h3>Traffic Density Legend</h3>
          <div className="legend">
            <div className="legend-item">
              <span className="color-box" style={{background: 'rgb(66, 153, 225)'}}></span>
              <span>Low Traffic</span>
            </div>
            <div className="legend-item">
              <span className="color-box" style={{background: 'rgb(239, 68, 68)'}}></span>
              <span>High Traffic</span>
            </div>
            <div className="legend-item">
              <span className="color-box" style={{background: '#10b981'}}></span>
              <span>Best Route</span>
            </div>
          </div>
        </div>
        <div className="info-card">
          <div className="update-info">
            <span>Last updated: {lastUpdate}</span>
            <span>Next image update: {nextUpdate}s</span>
            <button onClick={fetchGraphData} className="refresh-btn">🔄 Refresh</button>
          </div>
        </div>
      </div>
      <div className="graph-wrapper">
        <div ref={containerRef} className="network-container"></div>
      </div>
    </div>
  );
};

export default TrafficGraph;
