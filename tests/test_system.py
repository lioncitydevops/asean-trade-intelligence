"""
Automated validation test suite for ASEAN Trade, Energy & Supply Chain Intelligence Platform.
"""

import os
import pytest
from starlette.testclient import TestClient
from src.core.geofences import GEOFENCES, check_active_geofences
from src.data.historical_baselines import generate_time_series_data
from src.data.ais_stream import AISStreamEngine
from src.analytics.traffic_engine import TrafficAnalyticsEngine
from src.analytics.dark_fleet_detector import DarkFleetDetector
from src.analytics.maritime_engine import maritime_engine
from src.analytics.energy_engine import energy_engine
from src.analytics.supply_chain_engine import supply_chain_engine
from src.analytics.macro_nowcast_engine import macro_nowcast_engine
from src.analytics.carbon_engine import carbon_engine
from src.analytics.working_capital_engine import working_capital_engine
from src.analytics.chain_of_intelligence import chain_of_intelligence
from src.engine.narrative_generator import MacroNarrativeGenerator
from src.engine.pdf_generator import build_macro_newsletter_pdf
from src.api.server import app


def test_asean_geofencing():
    # Singapore Strait coordinate: Lat 1.25, Lon 103.8
    fences_sg = check_active_geofences(1.25, 103.8)
    assert "SINGAPORE_STRAIT" in fences_sg

    # Sunda Strait coordinate: Lat -6.0, Lon 105.8
    fences_sunda = check_active_geofences(-6.0, 105.8)
    assert "SUNDA_STRAIT" in fences_sunda


def test_six_engines():
    ais = AISStreamEngine()
    positions = ais.step_simulation(delta_minutes=15.0)

    # 1. Maritime Flow
    m_res = maritime_engine.analyze_maritime_flow(positions)
    assert m_res["total_vessels_tracked"] > 0
    assert "malacca_strait_vessels" in m_res["asean_chokepoints"]

    # 2. Energy Intelligence
    e_res = energy_engine.get_summary()
    assert e_res["state"]["brent_prompt_usd"] > 0
    assert e_res["state"]["tapis_asean_usd"] > 0

    # 3. Supply Chain Risk Intelligence
    r_res = supply_chain_engine.get_summary()
    assert r_res["state"]["malacca_bottleneck_risk_score"] > 0

    # 4. Macro Nowcasting
    mn_res = macro_nowcast_engine.get_summary()
    assert mn_res["state"]["asean_maritime_trade_volume_index"] > 100

    # 5. Carbon Intelligence
    c_res = carbon_engine.get_summary(positions)
    assert c_res["state"]["daily_regional_freight_co2_tonnes"] > 0

    # 6. Working Capital Intelligence
    wc_res = working_capital_engine.get_summary()
    assert wc_res["state"]["transit_inventory_cash_lockup_usd_millions"] > 1000.0


def test_chain_of_intelligence_cascade():
    ais = AISStreamEngine()
    positions = ais.step_simulation(delta_minutes=15.0)
    cascade = chain_of_intelligence.synthesize_cascade(positions)
    assert len(cascade.steps) == 6
    assert cascade.steps[0].step_number == 1
    assert "WHAT IS MOVING" in cascade.steps[0].stage_name
    assert "WHAT MANAGEMENT SHOULD INVESTIGATE" in cascade.steps[5].stage_name


def test_narrative_generator_fallback():
    generator = MacroNarrativeGenerator()
    summary = generator.generate_report_content(as_of_date="2026-09-16", gemini_api_key=None, force_ai=False)
    assert summary.title is not None
    assert len(summary.executive_summary_paragraphs) > 0
    assert "maritime" in summary.sections
    assert "risk_macro" in summary.sections
    assert "cash_carbon" in summary.sections
    assert "chain_action" in summary.sections


def test_api_endpoints_and_engines():
    with TestClient(app) as client:
        # 1. Health check
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        # 2. Engine endpoints
        res_m = client.get("/api/engines/maritime")
        assert res_m.status_code == 200
        assert "total_vessels_tracked" in res_m.json()

        res_e = client.get("/api/engines/energy")
        assert res_e.status_code == 200
        assert "state" in res_e.json()

        res_c = client.get("/api/chain-of-intelligence")
        assert res_c.status_code == 200
        assert "steps" in res_c.json()

        # 3. WebSocket endpoint
        with client.websocket_connect("/ws/telemetry") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "TELEMETRY_SNAPSHOT"
            assert "vessels" in data["data"]
            assert "engines" in data["data"]


def test_pdf_compilation():
    test_pdf = "output/test_output.pdf"
    if os.path.exists(test_pdf):
        os.remove(test_pdf)

    out = build_macro_newsletter_pdf(output_pdf_path=test_pdf, as_of_date="2026-09-16")
    assert os.path.exists(out)
    assert os.path.getsize(out) > 50000
