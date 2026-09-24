"""
Gemini 2.5 / 3.0 Flash & Pro AI Macro Intelligence Synthesizer.
Synthesizes real-time maritime telemetry, dark fleet anomalies, chokepoint baselines,
and crude forward curves into an institutional macroeconomic research newsletter.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List
from ..core.models import MacroInsightsSummary

logger = logging.getLogger(__name__)


def generate_gemini_macro_report(
    metrics: Dict[str, Any],
    market: Dict[str, Any],
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    as_of_date: str = "2026-09-16"
) -> MacroInsightsSummary:
    """
    Sends real-time telemetry metrics to Google Gemini 2.5 / 3.0 Flash/Pro to perform
    macroeconomic nowcasting and produce an institutional research newsletter.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ValueError(
            "Gemini API key is required. Please provide an API key in the report modal or set the GEMINI_API_KEY environment variable."
        )

    from ..analytics.energy_engine import energy_engine
    from ..analytics.supply_chain_engine import supply_chain_engine
    from ..analytics.macro_nowcast_engine import macro_nowcast_engine
    from ..analytics.carbon_engine import carbon_engine
    from ..analytics.working_capital_engine import working_capital_engine
    from ..analytics.chain_of_intelligence import chain_of_intelligence
    from ..data.ais_stream import stream_engine

    positions = stream_engine.step_simulation(delta_minutes=0.0)
    e_state = energy_engine.get_energy_state()
    r_state = supply_chain_engine.get_risk_state()
    mn_state = macro_nowcast_engine.get_macro_state()
    c_state = carbon_engine.calculate_carbon_state(positions)
    wc_state = working_capital_engine.get_working_capital_state()
    chain_cascade = chain_of_intelligence.synthesize_cascade(positions)

    prompt = f"""
You are the Chief ASEAN Trade Economist and Head of Quantitative Supply Chain Intelligence.
You are tasked with analyzing real-time maritime AIS telemetry, ASEAN chokepoints (Malacca, Singapore, Sunda, Lombok, South China Sea), energy crack spreads, Scope 3 carbon emissions, and corporate working capital drag to produce an authoritative, multi-engine institutional research briefing dated {as_of_date}.

=== REAL-TIME MULTI-ENGINE TELEMETRY (AS OF {as_of_date}) ===
1. MARITIME FLOW:
- Active AIS Vessels Tracked: {len(positions)}
- Strait of Malacca / Singapore / SCS Corridor: Active container, tanker, LNG carrier flows.

2. ENERGY INTELLIGENCE:
- Brent Prompt: ${e_state.brent_prompt_usd}/bbl | Tapis ASEAN Crude Premium: ${e_state.tapis_asean_usd}/bbl
- Singapore Gasoil 10ppm Crack Spread: ${e_state.singapore_gasoil_crack_usd}/bbl
- JKM Spot LNG: ${e_state.jkm_spot_lng_usd}/MMBtu
- Singapore Commercial Stocks: {e_state.singapore_onshore_stocks_mbbls}M bbls | Floating Storage: {e_state.fujairah_asean_floating_storage_mbbls}M bbls

3. SUPPLY CHAIN RISK & BOTTLENECKS:
- Malacca Bottleneck Risk Score: {r_state.malacca_bottleneck_risk_score}/100
- Cape Diversion Delay: +{r_state.cape_diversion_delay_days} days to ASEAN trade routes
- Singapore Container Berth Dwell: {r_state.singapore_container_dwell_days} days | Port Klang Wait: {r_state.port_klang_anchorage_wait_hours} hours

4. MACRO NOWCASTING:
- ASEAN Maritime Trade Volume Index (AMTVI): {mn_state.asean_maritime_trade_volume_index} (+{mn_state.amtvi_yoy_pct}% YoY)
- Regional Manufacturing PMI Nowcast: {mn_state.asean_pmi_nowcast}

5. CARBON INTELLIGENCE:
- Scope 3 Transport Emissions: {c_state.daily_regional_freight_co2_tonnes} tonnes CO2e/day
- Route Diversion CO2 Penalty: +{c_state.route_diversion_co2_penalty_pct}% per cargo delivered

6. WORKING CAPITAL INTELLIGENCE:
- Transit Inventory Cash Lockup: ${wc_state.transit_inventory_cash_lockup_usd_millions}M
- Cash Conversion Cycle (CCC) Expansion: +{wc_state.cash_conversion_cycle_expansion_days} days
- Supply Chain Finance (SCF) Liquidity Gap: ${wc_state.scf_liquidity_gap_usd_millions}M

Return a JSON object with title, subtitle, executive_summary_paragraphs, and sections (maritime, risk_macro, cash_carbon, chain_action).
"""

    models_to_try: List[str] = [
        model_name,
        "gemini-2.5-flash",
        "gemini-3.0-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-1.5-pro"
    ]
    seen = set()
    models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

    last_error = None
    for model in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.35,
                    "responseMimeType": "application/json"
                }
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text)

                return MacroInsightsSummary(
                    edition_date=as_of_date,
                    title=parsed.get("title", "HORMUZ IN THE DARK: WHAT MARITIME DATA REVEALS ABOUT GULF OIL FLOWS"),
                    subtitle=parsed.get("subtitle", "NEWSLETTER 2026 | SEPTEMBER EDITION | MACRO INSIGHTS"),
                    crude_futures_price=market.get("dec_horizon_price", 101.20),
                    curve_structure=market.get("forward_curve_structure", "Inverted / Steep Backwardation"),
                    hormuz_active_vessels_today=h.get("active_vessels_counted", 2),
                    hormuz_active_capacity_mbbls=h.get("active_capacity_mbbls", 2.0),
                    hormuz_baseline_vessels=h.get("baseline_vessels", 46),
                    hormuz_baseline_capacity_mbbls=h.get("baseline_capacity_mbbls", 19.0),
                    hormuz_dark_crossings_today=h.get("dark_crossings_estimated", 30),
                    fujairah_anchored_tankers=f.get("tankers_anchored_today", 61),
                    fujairah_anchored_capacity_mbbls=f.get("capacity_mbbls", 8.2),
                    fujairah_turnover_outflow_pct=f.get("turnover_outflow_offset_pct", 50.0),
                    bab_el_mandeb_7day_ma=b.get("seven_day_ma", 9.0),
                    suez_canal_7day_ma=s.get("seven_day_ma", 21.0),
                    petroline_status="Shut down (Drone strike)",
                    yanbu_daily_outflow_mbbls=0.0,
                    china_demand_reduction_pct=d.get("china_reduction_pct", 41.0),
                    india_demand_index=d.get("india", 142.5),
                    japan_demand_index=d.get("japan", 92.1),
                    skorea_demand_index=d.get("skorea", 109.6),
                    executive_summary_paragraphs=parsed.get("executive_summary_paragraphs", []),
                    sections=parsed.get("sections", {})
                )
        except Exception as e:
            logger.warning(f"Failed generation with {model}: {e}")
            last_error = e
            continue

    raise RuntimeError(f"Failed to generate report using Gemini API models ({models_to_try}): {last_error}")
