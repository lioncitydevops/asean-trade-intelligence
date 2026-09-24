import sys
import os
from pathlib import Path
from fastapi import FastAPI

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

app = FastAPI()

status_report = {}

# Test 1: Models & Geofences
try:
    from src.core.models import AISPosition, STSCluster
    from src.core.geofences import GEOFENCES
    status_report["core"] = "OK"
except Exception as e:
    status_report["core"] = str(e)

# Test 2: Data AIS Stream & Market Feed
try:
    from src.data.ais_stream import stream_engine
    from src.data.market_feed import get_market_intelligence
    status_report["data"] = "OK"
except Exception as e:
    status_report["data"] = str(e)

# Test 3: Analytics Engines
try:
    from src.analytics.maritime_engine import maritime_engine
    from src.analytics.energy_engine import energy_engine
    from src.analytics.supply_chain_engine import supply_chain_engine
    from src.analytics.macro_nowcast_engine import macro_nowcast_engine
    from src.analytics.carbon_engine import carbon_engine
    from src.analytics.working_capital_engine import working_capital_engine
    from src.analytics.chain_of_intelligence import chain_of_intelligence
    status_report["analytics"] = "OK"
except Exception as e:
    status_report["analytics"] = str(e)

# Test 4: Gemini Narratives & ReportLab PDF Generator
try:
    from src.engine.narrative_generator import narrative_generator
    from src.engine.pdf_generator import build_macro_newsletter_pdf
    status_report["engine"] = "OK"
except Exception as e:
    status_report["engine"] = str(e)

# Test 5: Full server import
try:
    import src.api.server as srv
    status_report["server_import"] = "OK"
except Exception as e:
    status_report["server_import"] = str(e)


@app.get("/api/health")
@app.get("/health")
def health():
    return {
        "status": "diagnostic",
        "modules": status_report
    }
