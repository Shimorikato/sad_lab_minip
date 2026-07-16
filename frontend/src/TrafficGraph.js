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
  const [srcNode, setSrcNode] = useState('J1');
  const [dstNode, setDstNode] = useState('J30');
  const [isDarkMode, setIsDarkMode] = useState(() => {
    try {
      const saved = localStorage.getItem('tms_dark_mode');
      return saved ? JSON.parse(saved) : false;
    } catch {
      return false;
    }
  });

  const fetchGraphData = async () => {
    try {
      const qs = new URLSearchParams({ src: srcNode, dst: dstNode }).toString();
      const response = await fetch(`/api/graph_data?${qs}`);
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
      setError(err.message || String(err));
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphData();
    const interval = setInterval(fetchGraphData, 1000);
    return () => clearInterval(interval);
  }, [srcNode, dstNode]);

  useEffect(() => {
    try {
      localStorage.setItem('tms_dark_mode', JSON.stringify(isDarkMode));
    } catch {}
  }, [isDarkMode]);

  useEffect(() => {
    if (!graphData || !containerRef.current) return;

    const COLORS = {
      low: '#4b84c6a8',       //blue
      medium: '#a48821ff',    // yellow
      high: '#c21a1ac2',      // red
      veryHigh: '#962222cb',  // dark red
      bestRoute: '#57b535ff'  //  green
    };

    const getColorForWeight = (weight, minWeight, maxWeight) => {
      if (maxWeight === minWeight) return COLORS.low;
      const normalized = (weight - minWeight) / Math.max(1, (maxWeight - minWeight));
      if (normalized <= 0.33) return COLORS.low;
      if (normalized <= 0.66) return COLORS.medium;
      if (normalized <= 0.85) return COLORS.high;
      return COLORS.veryHigh;
    };

    const { nodes, edges, best_route, min_weight, max_weight } = graphData;

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

    const nodesDataset = nodes.map(n => {
      const hasBackendPos = typeof n.x === 'number' && typeof n.y === 'number';
      const preset = nodePositions[n.id];
      const x = hasBackendPos ? n.x : (preset ? preset.x : undefined);
      const y = hasBackendPos ? n.y : (preset ? preset.y : undefined);
      const fixed = (hasBackendPos || preset) ? { x: true, y: true } : false;
      return {
        id: n.id,
        label: n.label,
        shape: 'dot',
        size: 15,
        ...(x !== undefined ? { x } : {}),
        ...(y !== undefined ? { y } : {}),
        fixed,
      color: isDarkMode ? {
        background: '#2b2f36',
        border: '#8ab4f8',
        highlight: { background: '#374151', border: '#93c5fd' }
      } : {
        background: '#667eea',
        border: '#764ba2',
        highlight: { background: '#f59e0b', border: '#d97706' }
      },
      font: isDarkMode ? { color: '#e5e7eb', size: 16, face: 'Arial', bold: true }
                       : { color: '#1a202c', size: 16, face: 'Arial', bold: true }
      };
    });

    const onBestRoute = (from, to) => {
      if (!Array.isArray(best_route) || best_route.length < 2) return false;
      for (let i = 0; i < best_route.length - 1; i++) {
        const a = best_route[i];
        const b = best_route[i + 1];
        if ((a === from && b === to) || (a === to && b === from)) return true;
      }
      return false;
    };

    const edgesDataset = edges.map(e => {
      const isOnBestRoute = onBestRoute(e.from, e.to);
      const baseColor = isOnBestRoute ? COLORS.bestRoute : getColorForWeight(e.weight, min_weight, max_weight);
      const isGreen = baseColor.toLowerCase() === COLORS.low.toLowerCase() || baseColor.toLowerCase() === COLORS.bestRoute.toLowerCase();

      return {
        from: e.from,
        to: e.to,
        label: (typeof e.count === 'number') ? `${e.count} vehicles` : `${Math.round(e.weight)} vehicles`,
        color: {
          color: baseColor,
          highlight: isDarkMode ? '#fbbf24' : '#f59e0b',
          opacity: 0.9
        },
        width: isOnBestRoute ? 5 : 3,
        shadow: isGreen ? { enabled: true, color: isDarkMode ? 'rgba(34,197,94,0.5)' : 'rgba(16,185,129,0.45)', size: 10, x: 0, y: 0 } : false,
        smooth: { type: 'continuous', roundness: 0.5 },
        font: { color: isDarkMode ? '#e5e7eb' : '#1a202c', size: 12, background: isDarkMode ? '#111827' : 'white', strokeWidth: 0 },
        arrows: { to: { enabled: false } }
      };
    });

    const data = { nodes: nodesDataset, edges: edgesDataset };

    const options = {
      physics: { enabled: false },
      interaction: { hover: true, tooltipDelay: 100, zoomView: true, dragView: true },
      layout: { hierarchical: false },
      edges: { smooth: { type: 'continuous', roundness: 0.2 } }
    };

    if (networkRef.current) {
      const currentPosition = networkRef.current.getViewPosition();
      const currentScale = networkRef.current.getScale();
      networkRef.current.setData(data);
      networkRef.current.moveTo({ position: currentPosition, scale: currentScale, animation: false });
    } else {
      networkRef.current = new Network(containerRef.current, data, options);
    }
  }, [graphData, isDarkMode]);

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
    <div className={`traffic-graph-container ${isDarkMode ? 'dark' : ''}`}>
      <div className="info-panel">
        <div className="info-card">
          <button
            className="theme-toggle"
            onClick={() => setIsDarkMode(v => !v)}
            aria-label="Toggle dark mode"
            title="Toggle dark mode"
          >
            {isDarkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
          </button>
        </div>
        <div className="info-card">
          <h3>Route Finder</h3>
          <div className="route-form">
            <div className="route-inputs">
              <label>
                From
                <input list="nodes-list" value={srcNode} onChange={e => setSrcNode(e.target.value)} placeholder="J1" />
              </label>
              <label>
                To
                <input list="nodes-list" value={dstNode} onChange={e => setDstNode(e.target.value)} placeholder="J10" />
              </label>
              <button onClick={fetchGraphData} className="find-btn">Find route</button>
            </div>
            <datalist id="nodes-list">
              {graphData?.nodes?.map(n => (
                <option key={n.id} value={n.id}>{n.label}</option>
              ))}
            </datalist>
          </div>
        </div>
        <div className="info-card">
          <h3>Best Route (Least Congested)</h3>
          <div className="route-path">{graphData?.best_route?.join(' → ')}</div>
        </div>
        {/* <div className="info-card">
          <h3>Traffic Density Legend</h3>
          <div className="legend">
            <div className="legend-item">
              <span className="color-box" style={{ background: '#10b981' }}></span>
              <span>Low (Green)</span>
            </div>
            <div className="legend-item">
              <span className="color-box" style={{ background: '#f59e0b' }}></span>
              <span>Medium (Yellow)</span>
            </div>
            <div className="legend-item">
              <span className="color-box" style={{ background: '#f97316' }}></span>
              <span>High (Orange)</span>
            </div>
            <div className="legend-item">
              <span className="color-box" style={{ background: '#ef4444' }}></span>
              <span>Very High (Red)</span>
            </div>
            <div className="legend-item">
              <span className="color-box" style={{ background: '#22c55e' }}></span>
              <span>Best Route</span>
            </div>
          </div>
        </div> */}
        <div className="info-card">
          <div className="update-info">
            <span>Last updated: {lastUpdate}</span>
            {/* <span>Next image update: {nextUpdate}s</span> */}
            {/* <button onClick={fetchGraphData} className="refresh-btn">🔄 Refresh</button> */}
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
