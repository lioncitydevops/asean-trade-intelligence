# Technical Specification: Maritime Oil Flow Intelligence Platform Upgrades

**Document Version**: 2.0.0  
**Author**: Autonomous Product Manager (@pm) & Lead Quantitative Architect  
**Status**: Approved for Execution  
**Target Date**: 2026-09-23  

---

## 1. Executive Summary & Objective

This specification details four high-impact enhancements to the **Maritime Oil Flow Intelligence & Real-Time Macro Nowcasting Platform**:

1. **Interactive Geospatial Visualizer (`app.js`, `index.html`, `styles.css`)**: Dynamic vessel motion trails, pulsing radar rings for Dark Fleet & STS anomalies, choke-point density heatmaps/zones, and quick-focus camera presets for major global choke points.
2. **Gemini 2.5 / 3.0 Flash Macro AI Synthesizer (`gemini_synthesizer.py`)**: Institutional research commentary with quantitative forward curve forecasting, prompt-M+6 backwardation modeling, and structured macro forecasts.
3. **Real-Time WebSocket Streaming Engine (`server.py`, `app.js`)**: Bi-directional `/ws/telemetry` streaming pipeline pushing live vessel coordinates, STS rendezvous alerts, and market ticks with automatic HTTP polling fallback.
4. **Cloud Run & Docker Continuous Deployment (`Dockerfile`, `deploy/`)**: Production-hardened containerization, dependency lock, automated deployment scripts, and CI/CD validation.

---

## 2. Component Specifications

### A. Interactive Geospatial Visualizer
- **Dynamic Vessel Trails**: Breadcrumb polyline trails tracking the last 5-10 position ticks with opacity fade to visualize velocity and heading.
- **Dark Fleet Pulsing Rings**: Animated CSS radar pulse (`@keyframes radar-pulse`) for vessels with AIS transponders disabled or engaged in clandestine STS operations.
- **Choke-Point Density Heatmaps & Visual Zones**: Semi-transparent density rings with dynamic vessel count badges around Hormuz, Fujairah, Bab el-Mandeb, Malacca, and Suez.
- **Map Toolbar & Controls**:
  - Layer toggles: `[Trails]`, `[Choke Density]`, `[Geofences]`.
  - Quick-zoom presets: `[Global]`, `[Strait of Hormuz]`, `[Fujairah STS]`, `[Red Sea & Bab el-Mandeb]`, `[Malacca Strait]`.

### B. Gemini 2.5 / 3.0 Flash Macro AI Synthesizer
- **Multi-Model Support**: Support `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-3.0-flash`, and `gemini-2.0-flash`.
- **Structured Macro Output**:
  - Executive summary with prompt/horizon pricing paradox.
  - Section 1: Hormuz clandestine telemetry and Fujairah STS transshipment offset analysis.
  - Section 2: Red Sea / Petroline disruption divergence.
  - Section 3: Asian seaborne demand nowcast (China SPR buffer vs India opportunistic buying).
  - Section 4: Quantitative 6-month Brent curve forward structure & trade positioning.
- **Resilience**: Robust multi-tier fallback ensuring institutional quality output even in restricted environments.

### C. Real-Time WebSocket Streaming Engine
- **FastAPI WebSocket Endpoint**: `/ws/telemetry`
- **Connection Manager**: Broadcasts simulation state every 2.5 seconds to all connected clients.
- **Event Dispatching**: Instant alert packet when a new STS operation or Dark Fleet transponder disabling event is detected.
- **Frontend Client (`app.js`)**: Auto-reconnecting WebSocket client with live status indicator (WebSocket Connected vs HTTP Polling fallback).

### D. Docker & Cloud Run Deployment Hardening
- **Containerization**: Python 3.11/3.12 slim base with `uvicorn[standard]`, `websockets`, `reportlab`, `pandas`, `numpy`, and system fonts.
- **Health Checks & Scripts**: Automated PowerShell (`deploy_cloud_run.ps1`) and Bash (`deploy_cloud_run.sh`) scripts.

---

## 3. API & Data Contracts

### WebSocket Packet (`/ws/telemetry`)
```json
{
  "type": "TELEMETRY_TICK",
  "timestamp": "2026-09-23T03:00:00Z",
  "data": {
    "vessels": [...],
    "metrics": {...},
    "market": {...},
    "sts_clusters": [...],
    "dark_events": [...]
  }
}
```

---

## 4. Verification & Testing Plan
1. **Unit & Integration Tests**: `pytest tests/` covering WebSocket connection management, Gemini synthesis fallback, and geospatial coordinate bounds.
2. **Diagnostics**: `python main.py --test` verifying telemetry math and anomaly algorithms.
3. **Browser Verification**: Interactive map with real-time animated trails, pulsing dark fleet markers, and live WebSocket connection.
