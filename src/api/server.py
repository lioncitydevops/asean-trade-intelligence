"""
FastAPI Backend Server providing real-time telemetry APIs, WebSocket streaming endpoints,
and automated report generation services.
"""

import os
import asyncio
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path

# Ensure project root is in sys.path
_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from ..core.models import AISPosition, STSCluster
    from ..core.geofences import GEOFENCES
    from ..data.ais_stream import stream_engine
    from ..data.market_feed import get_market_intelligence
    from ..analytics.traffic_engine import traffic_engine
    from ..analytics.dark_fleet_detector import dark_fleet_detector
    from ..analytics.maritime_engine import maritime_engine
    from ..analytics.energy_engine import energy_engine
    from ..analytics.supply_chain_engine import supply_chain_engine
    from ..analytics.macro_nowcast_engine import macro_nowcast_engine
    from ..analytics.carbon_engine import carbon_engine
    from ..analytics.working_capital_engine import working_capital_engine
    from ..analytics.chain_of_intelligence import chain_of_intelligence
    from ..engine.narrative_generator import narrative_generator
    from ..engine.pdf_generator import build_macro_newsletter_pdf
except (ImportError, ValueError):
    from src.core.models import AISPosition, STSCluster
    from src.core.geofences import GEOFENCES
    from src.data.ais_stream import stream_engine
    from src.data.market_feed import get_market_intelligence
    from src.analytics.traffic_engine import traffic_engine
    from src.analytics.dark_fleet_detector import dark_fleet_detector
    from src.analytics.maritime_engine import maritime_engine
    from src.analytics.energy_engine import energy_engine
    from src.analytics.supply_chain_engine import supply_chain_engine
    from src.analytics.macro_nowcast_engine import macro_nowcast_engine
    from src.analytics.carbon_engine import carbon_engine
    from src.analytics.working_capital_engine import working_capital_engine
    from src.analytics.chain_of_intelligence import chain_of_intelligence
    from src.engine.narrative_generator import narrative_generator
    from src.engine.pdf_generator import build_macro_newsletter_pdf

logger = logging.getLogger("maritime_server")


class ConnectionManager:
    """Manages active WebSocket client connections for real-time AIS broadcasting."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast_json(self, message: Dict[str, Any]):
        if not self.active_connections:
            return

        to_remove = set()
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.debug(f"Error sending to WebSocket client: {e}")
                to_remove.add(connection)

        for dead_conn in to_remove:
            self.active_connections.discard(dead_conn)


manager = ConnectionManager()
broadcaster_task: Optional[asyncio.Task] = None


def serialize_model(obj: Any) -> Any:
    """Helper to serialize Pydantic v1 / v2 models safely for JSON and WebSockets."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    if hasattr(obj, "dict"):
        return obj.dict()
    return obj


async def telemetry_broadcast_loop():
    """Background async loop stepping simulation and pushing live telemetry to WebSocket clients."""
    while True:
        try:
            await asyncio.sleep(2.5)
            if manager.active_connections:
                positions = stream_engine.step_simulation(delta_minutes=15.0)
                sts_clusters = dark_fleet_detector.detect_sts_operations(positions)
                dark_events = dark_fleet_detector.detect_dark_transponders(positions)
                metrics = traffic_engine.get_current_metrics(positions=positions)
                market = get_market_intelligence()

                payload = {
                    "type": "TELEMETRY_TICK",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "count": len(positions),
                        "vessels": [serialize_model(p) for p in positions],
                        "active_sts_clusters": [serialize_model(c) for c in sts_clusters],
                        "dark_fleet_events": dark_events,
                        "metrics": metrics,
                        "market": market
                    }
                }
                await manager.broadcast_json(payload)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in telemetry broadcast loop: {e}")
            await asyncio.sleep(2.5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global broadcaster_task
    is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
    if not is_serverless:
        try:
            broadcaster_task = asyncio.create_task(telemetry_broadcast_loop())
        except Exception as e:
            logger.warning(f"Could not start background broadcast loop: {e}")
    yield
    if broadcaster_task:
        broadcaster_task.cancel()
        try:
            await broadcaster_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="ASEAN Trade, Energy & Supply Chain Intelligence Platform",
    description="Multi-engine real-time AIS telemetry analysis, energy pricing, supply chain risk, carbon tracking, working capital drag, and macro nowcasting.",
    version="3.0.0",
    lifespan=lifespan
)

# Enable CORS for interactive UI development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """
    Real-time WebSocket endpoint streaming AIS positions, STS events, market feeds, and engine telemetry.
    """
    await manager.connect(websocket)
    try:
        # Send initial snapshot immediately upon connection
        positions = stream_engine.step_simulation(delta_minutes=0.0)
        sts_clusters = dark_fleet_detector.detect_sts_operations(positions)
        dark_events = dark_fleet_detector.detect_dark_transponders(positions)
        metrics = traffic_engine.get_current_metrics(positions=positions)
        market = get_market_intelligence()
        maritime_flow = maritime_engine.analyze_maritime_flow(positions)
        energy_intel = energy_engine.get_summary()
        supply_chain_intel = supply_chain_engine.get_summary()
        macro_nowcast = macro_nowcast_engine.get_summary()
        carbon_intel = carbon_engine.get_summary(positions)
        working_capital_intel = working_capital_engine.get_summary()
        cascade = chain_of_intelligence.synthesize_cascade(positions)

        initial_packet = {
            "type": "TELEMETRY_SNAPSHOT",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "count": len(positions),
                "vessels": [serialize_model(p) for p in positions],
                "active_sts_clusters": [serialize_model(c) for c in sts_clusters],
                "dark_fleet_events": dark_events,
                "metrics": metrics,
                "market": market,
                "engines": {
                    "maritime": maritime_flow,
                    "energy": energy_intel,
                    "supply_chain": supply_chain_intel,
                    "macro_nowcast": macro_nowcast,
                    "carbon": carbon_intel,
                    "working_capital": working_capital_intel,
                },
                "chain_cascade": serialize_model(cascade)
            }
        }
        await websocket.send_json(initial_packet)

        while True:
            # Keep listening for client heartbeats/pings
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_json({"type": "PONG", "timestamp": datetime.now(timezone.utc).isoformat()})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.debug(f"WebSocket session closed: {e}")
        manager.disconnect(websocket)


@app.get("/api/health")
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "platform": "ASEAN Trade, Energy & Supply Chain Intelligence",
        "version": "3.0.0",
        "ws_clients": len(manager.active_connections),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/ai-status")
@app.get("/ai-status")
async def get_ai_status():
    """Returns whether a server-side Gemini API key is configured."""
    has_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    return {
        "ai_enabled": has_key,
        "default_model": "gemini-2.5-flash",
        "supported_models": ["gemini-2.5-flash", "gemini-3.0-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/metrics")
@app.get("/metrics")
async def get_live_metrics():
    """Returns current real-time headline metrics and market state."""
    positions = stream_engine.step_simulation(delta_minutes=0.0)
    metrics = traffic_engine.get_current_metrics(positions=positions)
    market = get_market_intelligence()
    return {
        "metrics": metrics,
        "market": market,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/vessels")
@app.get("/vessels")
async def get_live_vessels():
    """Steps simulation and returns real-time positions for all vessels."""
    positions = stream_engine.step_simulation(delta_minutes=15.0)
    sts_clusters = dark_fleet_detector.detect_sts_operations(positions)
    dark_events = dark_fleet_detector.detect_dark_transponders(positions)
    metrics = traffic_engine.get_current_metrics(positions=positions)
    market = get_market_intelligence()

    return {
        "count": len(positions),
        "vessels": [serialize_model(p) for p in positions],
        "active_sts_clusters": [serialize_model(c) for c in sts_clusters],
        "dark_fleet_events": dark_events,
        "metrics": metrics,
        "market": market,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/engines/maritime")
@app.get("/engines/maritime")
async def get_maritime_engine():
    """Engine 1: Maritime Flow Intelligence."""
    positions = stream_engine.step_simulation(delta_minutes=0.0)
    return maritime_engine.analyze_maritime_flow(positions)


@app.get("/api/engines/energy")
@app.get("/engines/energy")
async def get_energy_engine():
    """Engine 2: Energy Intelligence."""
    return energy_engine.get_summary()


@app.get("/api/engines/supply-chain")
@app.get("/engines/supply-chain")
async def get_supply_chain_engine():
    """Engine 3: Supply Chain Risk Intelligence."""
    return supply_chain_engine.get_summary()


@app.get("/api/engines/macro-nowcast")
@app.get("/engines/macro-nowcast")
async def get_macro_nowcast_engine():
    """Engine 4: Macro Nowcasting."""
    return macro_nowcast_engine.get_summary()


@app.get("/api/engines/carbon")
@app.get("/engines/carbon")
async def get_carbon_engine():
    """Engine 5: Carbon Intelligence."""
    positions = stream_engine.step_simulation(delta_minutes=0.0)
    return carbon_engine.get_summary(positions)


@app.get("/api/engines/working-capital")
@app.get("/engines/working-capital")
async def get_working_capital_engine():
    """Engine 6: Working Capital Intelligence."""
    return working_capital_engine.get_summary()


@app.get("/api/chain-of-intelligence")
@app.get("/chain-of-intelligence")
async def get_chain_of_intelligence():
    """The 6-Step Chain of Intelligence Cascade."""
    positions = stream_engine.step_simulation(delta_minutes=0.0)
    cascade = chain_of_intelligence.synthesize_cascade(positions)
    return serialize_model(cascade)


@app.get("/api/geofences")
@app.get("/geofences")
async def get_geofences():
    """Returns coordinates and descriptions of all monitored maritime chokepoint zones."""
    fences = []
    for code, g in GEOFENCES.items():
        fences.append({
            "code": code,
            "name": g.name,
            "polygon": g.polygon,
            "description": g.description
        })
    return {"geofences": fences}


@app.get("/api/exhibits/data")
@app.get("/exhibits/data")
async def get_exhibits_data():
    """Returns structured time series data for interactive frontend charts (Exhibits 1, 2, 3)."""
    fujairah = traffic_engine.get_fujairah_series()
    redsea = traffic_engine.get_redsea_series()
    asian_demand = traffic_engine.get_asian_demand_series()

    return {
        "exhibit_1": fujairah.to_dict(orient="records"),
        "exhibit_2": redsea.to_dict(orient="records"),
        "exhibit_3": asian_demand.to_dict(orient="records"),
    }


class ReportGenerationRequest(BaseModel):
    as_of_date: Optional[str] = "2026-09-16"
    gemini_api_key: Optional[str] = None
    model_name: Optional[str] = "gemini-2.5-flash"
    force_ai: Optional[bool] = False


def get_pdf_output_path() -> str:
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or not os.access(".", os.W_OK):
        return "/tmp/Macro_Insights_Newsletter_RealTime.pdf"
    os.makedirs("output", exist_ok=True)
    return "output/Macro_Insights_Newsletter_RealTime.pdf"


@app.post("/api/generate-report")
@app.post("/generate-report")
async def trigger_report_generation(req: Optional[ReportGenerationRequest] = None):
    """
    Synthesizes live telemetry and generates the institutional PDF report using Gemini AI.
    """
    if req is None:
        req = ReportGenerationRequest()

    output_pdf = get_pdf_output_path()

    # 1. Synthesize narrative using Gemini if key available
    summary = narrative_generator.generate_report_content(
        as_of_date=req.as_of_date or "2026-09-16",
        gemini_api_key=req.gemini_api_key,
        model_name=req.model_name or "gemini-2.5-flash",
        force_ai=req.force_ai or False
    )

    # 2. Compile PDF
    pdf_path = build_macro_newsletter_pdf(
        output_pdf_path=output_pdf,
        as_of_date=req.as_of_date or "2026-09-16",
        summary=summary
    )

    return {
        "status": "success",
        "message": "Real-time AI report generated successfully.",
        "pdf_path": pdf_path,
        "summary": serialize_model(summary),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/download-report")
@app.get("/download-report")
async def download_report():
    """Serves the latest compiled PDF newsletter."""
    pdf_path = get_pdf_output_path()
    if not os.path.exists(pdf_path):
        build_macro_newsletter_pdf(output_pdf_path=pdf_path)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="Macro_Insights_Newsletter_RealTime.pdf"
    )



# Mount static web frontend for local execution only (Vercel CDN handles static frontend)
is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if not is_serverless and os.path.exists(web_dir):
    app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
