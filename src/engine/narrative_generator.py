import os
import logging
from typing import Dict, Any, Optional
from ..core.models import MacroInsightsSummary
from ..analytics.traffic_engine import traffic_engine
from ..analytics.dark_fleet_detector import dark_fleet_detector
from ..data.market_feed import get_market_intelligence
from .gemini_synthesizer import generate_gemini_macro_report
from ..analytics.maritime_engine import maritime_engine
from ..analytics.energy_engine import energy_engine
from ..analytics.supply_chain_engine import supply_chain_engine
from ..analytics.macro_nowcast_engine import macro_nowcast_engine
from ..analytics.carbon_engine import carbon_engine
from ..analytics.working_capital_engine import working_capital_engine
from ..analytics.chain_of_intelligence import chain_of_intelligence
from ..data.ais_stream import stream_engine

logger = logging.getLogger(__name__)


class MacroNarrativeGenerator:
    def __init__(self):
        pass

    def generate_report_content(
        self,
        as_of_date: str = "2026-09-16",
        gemini_api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        force_ai: bool = False
    ) -> MacroInsightsSummary:
        """
        Synthesizes live telemetry, ASEAN trade flow, energy crack spreads, carbon emissions,
        working capital drag, and macro nowcasting into an institutional intelligence briefing.
        """
        metrics = traffic_engine.get_current_metrics()
        market = get_market_intelligence(as_of_date)
        positions = stream_engine.step_simulation(delta_minutes=0.0)

        # 6 Engines Data
        e_state = energy_engine.get_energy_state()
        r_state = supply_chain_engine.get_risk_state()
        mn_state = macro_nowcast_engine.get_macro_state()
        c_state = carbon_engine.calculate_carbon_state(positions)
        wc_state = working_capital_engine.get_working_capital_state()
        chain_cascade = chain_of_intelligence.synthesize_cascade(positions)

        key = gemini_api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

        if key or force_ai:
            try:
                return generate_gemini_macro_report(
                    metrics=metrics,
                    market=market,
                    api_key=key,
                    model_name=model_name,
                    as_of_date=as_of_date
                )
            except Exception as e:
                logger.error(f"Gemini generation error: {e}")
                if force_ai:
                    raise

        h = metrics["hormuz"]
        f = metrics["fujairah"]
        b = metrics["bab_el_mandeb"]
        s = metrics["suez_canal"]
        d = metrics["asian_demand_indices"]

        title = "ASEAN TRADE, ENERGY & SUPPLY CHAIN INTELLIGENCE BRIEFING"
        subtitle = "INSTITUTIONAL BRIEFING 2026 | MACRO NOWCASTING & MULTI-ENGINE CHAIN OF INTELLIGENCE"

        exec_summary = [
            f"Physical trade movements across ASEAN chokepoints signal a widening divergence between energy input costs and supply chain liquidity. "
            f"With Brent prompt crude at ${e_state.brent_prompt_usd}/bbl and Singapore Gasoil 10ppm crack spreads elevated at ${e_state.singapore_gasoil_crack_usd}/bbl, "
            f"regional logistics costs are increasing. Rerouting around the Cape of Good Hope adds +{r_state.cape_diversion_delay_days} days to Europe-ASEAN transit times, "
            f"locking up ${wc_state.transit_inventory_cash_lockup_usd_millions}M in floating working capital and generating {c_state.daily_regional_freight_co2_tonnes} tonnes of daily Scope 3 CO2e. "
            f"Our ASEAN Maritime Trade Volume Index (AMTVI) nowcasting at {mn_state.asean_maritime_trade_volume_index} (+{mn_state.amtvi_yoy_pct}% YoY) indicates robust regional trade velocity despite shipping bottlenecks."
        ]

        section_maritime = {
            "title": "Engine 1 & 2: Maritime Flow & Energy Intelligence",
            "paragraphs": [
                f"Physical vessel tracking shows strong container and tanker activity across the Strait of Malacca, Singapore Strait, and deepwater Lombok passage. "
                f"Bintulu LNG exports from Sarawak remain steady, supporting Singapore and East Asian energy security.",
                f"Tapis ASEAN sweet crude trades at a premium of ${e_state.tapis_asean_usd}/bbl, while Singapore onshore commercial oil stocks stand at {e_state.singapore_onshore_stocks_mbbls}M bbls. "
                f"Offshore floating storage across Fujairah and ASEAN hubs holds {e_state.fujairah_asean_floating_storage_mbbls}M bbls."
            ]
        }

        section_risk_macro = {
            "title": "Engine 3 & 4: Supply Chain Risk & Macro Nowcasting",
            "paragraphs": [
                f"The Malacca Strait Bottleneck Risk Score is rated at {r_state.malacca_bottleneck_risk_score}/100, driven by container berth dwell times of {r_state.singapore_container_dwell_days} days in Singapore and Port Klang anchorage wait times of {r_state.port_klang_anchorage_wait_hours} hours.",
                f"Primary sector exposure is concentrated in Semiconductor & Electronics assembly (Penang/Singapore, risk score 88.5) and Refining & Petrochemicals (Map Ta Phut/Jurong, risk score 82.0).",
                f"Despite transit delays, high-frequency macro nowcasting projects solid GDP contributions across key ASEAN economies (Malaysia +4.8%, Indonesia +5.1%, Singapore +2.6%)."
            ]
        }

        section_cash_carbon = {
            "title": "Engine 5 & 6: Carbon & Working Capital Intelligence",
            "paragraphs": [
                f"Cape of Good Hope rerouting diversions carry a severe Scope 3 carbon penalty of +{c_state.route_diversion_co2_penalty_pct}%, subjecting long-haul carriers to elevated carbon tax liabilities under EU CBAM (${c_state.cbam_carbon_tax_liability_usd_tonne}/tonne CO2e).",
                f"Financially, inventory transit delays expand corporate Cash Conversion Cycles (CCC) by +{wc_state.cash_conversion_cycle_expansion_days} days across regional trade corridors. "
                f"The resulting carrying cost penalty totals ${wc_state.inventory_carrying_cost_penalty_monthly_usd_millions}M per month, highlighting an urgent $1.2B Supply Chain Financing (SCF) liquidity gap for regional importers and exporters."
            ]
        }

        section_chain_action = {
            "title": "Chain of Intelligence: Actionable Management Strategy",
            "paragraphs": [
                f"1. WHAT IS MOVING: {chain_cascade.steps[0].headline}",
                f"2. WHAT HAS CHANGED: {chain_cascade.steps[1].headline}",
                f"3. WHY IT MATTERS: {chain_cascade.steps[2].headline}",
                f"4. WHICH COMPANY IS EXPOSED: {chain_cascade.steps[3].headline}",
                f"5. CASH & CARBON CONFLICT: {chain_cascade.steps[4].headline}",
                f"6. MANAGEMENT ACTION: {chain_cascade.steps[5].headline}"
            ]
        }

        return MacroInsightsSummary(
            edition_date=as_of_date,
            title=title,
            subtitle=subtitle,
            crude_futures_price=market["dec_horizon_price"],
            curve_structure=market["forward_curve_structure"],
            hormuz_active_vessels_today=h["active_vessels_counted"],
            hormuz_active_capacity_mbbls=h["active_capacity_mbbls"],
            hormuz_baseline_vessels=h["baseline_vessels"],
            hormuz_baseline_capacity_mbbls=h["baseline_capacity_mbbls"],
            hormuz_dark_crossings_today=h["dark_crossings_estimated"],
            fujairah_anchored_tankers=f["tankers_anchored_today"],
            fujairah_anchored_capacity_mbbls=f["capacity_mbbls"],
            fujairah_turnover_outflow_pct=f["turnover_outflow_offset_pct"],
            bab_el_mandeb_7day_ma=b["seven_day_ma"],
            suez_canal_7day_ma=s["seven_day_ma"],
            petroline_status="Monitoring",
            yanbu_daily_outflow_mbbls=0.0,
            china_demand_reduction_pct=d["china_reduction_pct"],
            india_demand_index=d["india"],
            japan_demand_index=d["japan"],
            skorea_demand_index=d["skorea"],
            energy_intel=e_state,
            risk_intel=r_state,
            macro_nowcast=mn_state,
            carbon_intel=c_state,
            working_capital_intel=wc_state,
            chain_of_intel=chain_cascade,
            executive_summary_paragraphs=exec_summary,
            sections={
                "maritime": section_maritime,
                "risk_macro": section_risk_macro,
                "cash_carbon": section_cash_carbon,
                "chain_action": section_chain_action,
            }
        )


# Singleton instance
narrative_generator = MacroNarrativeGenerator()

