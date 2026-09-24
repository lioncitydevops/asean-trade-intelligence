"""
Chain of Intelligence Cascade Synthesizer
Orchestrates the 6-step intelligence chain:
What is moving → What has changed → Why it matters → Which company/sector is exposed → What happens to cash & carbon → What management should investigate.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from .maritime_engine import maritime_engine
from .energy_engine import energy_engine
from .supply_chain_engine import supply_chain_engine
from .macro_nowcast_engine import macro_nowcast_engine
from .carbon_engine import carbon_engine
from .working_capital_engine import working_capital_engine
from ..core.models import AISPosition, ChainOfIntelligenceCascade, ChainOfIntelligenceStep


class ChainOfIntelligenceSynthesizer:
    def __init__(self):
        pass

    def synthesize_cascade(self, positions: List[AISPosition]) -> ChainOfIntelligenceCascade:
        m_intel = maritime_engine.analyze_maritime_flow(positions)
        e_state = energy_engine.get_energy_state()
        r_state = supply_chain_engine.get_risk_state()
        mn_state = macro_nowcast_engine.get_macro_state()
        c_state = carbon_engine.calculate_carbon_state(positions)
        wc_state = working_capital_engine.get_working_capital_state()

        steps = [
            ChainOfIntelligenceStep(
                step_number=1,
                stage_name="1. WHAT IS MOVING",
                headline=f"Tracking {m_intel['total_vessels_tracked']} Vessels & {m_intel['total_cargo_in_transit_mbbls']}M bbls across ASEAN Maritime Chokepoints",
                data_summary=f"Active transits focused on Strait of Malacca ({m_intel['asean_chokepoints']['malacca_strait_vessels']} vessels), Singapore Strait ({m_intel['asean_chokepoints']['singapore_strait_vessels']} vessels), and South China Sea corridor ({m_intel['asean_chokepoints']['south_china_sea_corridor']} vessels).",
                key_metrics={
                    "total_vessels": m_intel["total_vessels_tracked"],
                    "cargo_mbbls": m_intel["total_cargo_in_transit_mbbls"],
                    "malacca_vessels": m_intel["asean_chokepoints"]["malacca_strait_vessels"],
                },
                actionable_insight="Establish continuous real-time AIS radar monitoring across Malacca and Sunda chokepoints."
            ),
            ChainOfIntelligenceStep(
                step_number=2,
                stage_name="2. WHAT HAS CHANGED",
                headline=f"Cape Rerouting (+{r_state.cape_diversion_delay_days}d) + Gasoil Crack Spread at ${e_state.singapore_gasoil_crack_usd}/bbl",
                data_summary=f"Red Sea diversions force long-haul vessels to bypass Suez, causing a +{r_state.cape_diversion_delay_days}-day delay. Singapore container berth dwell times have risen to {r_state.singapore_container_dwell_days} days.",
                key_metrics={
                    "cape_delay_days": r_state.cape_diversion_delay_days,
                    "gasoil_crack_usd": e_state.singapore_gasoil_crack_usd,
                    "sg_container_dwell_days": r_state.singapore_container_dwell_days,
                },
                actionable_insight="Flag incoming cargo delays to procurement and re-route urgent shipments via deepwater Lombok passage."
            ),
            ChainOfIntelligenceStep(
                step_number=3,
                stage_name="3. WHY IT MATTERS",
                headline=f"Energy Security Input Pressure & AMTVI Nowcast at {mn_state.asean_maritime_trade_volume_index}",
                data_summary=f"Refining margins and freight rate surcharges add upward pressure to ASEAN import costs, while trade nowcasting signals strong industrial input velocity (+{mn_state.amtvi_yoy_pct}% YoY).",
                key_metrics={
                    "amtvi_index": mn_state.asean_maritime_trade_volume_index,
                    "amtvi_yoy": mn_state.amtvi_yoy_pct,
                    "tapis_crude_usd": e_state.tapis_asean_usd,
                },
                actionable_insight="Incorporate real-time physical trade nowcasts into quarterly economic and earnings forecasting models."
            ),
            ChainOfIntelligenceStep(
                step_number=4,
                stage_name="4. WHICH COMPANY / SECTOR IS EXPOSED",
                headline="High Exposure in Semiconductors (SG/MY), Refiners (Petronas/PTT/Pertamina) & Power Utilities",
                data_summary="Semiconductor plants in Penang & Singapore face component delays; Map Ta Phut and Jurong refineries experience feedstock arrival jitter.",
                key_metrics={
                    "semicon_exposure_score": r_state.top_exposed_sectors[0]["exposure_score"],
                    "refining_exposure_score": r_state.top_exposed_sectors[1]["exposure_score"],
                    "exposed_sectors_count": len(r_state.top_exposed_sectors),
                },
                actionable_insight="Audit tier-1 and tier-2 supplier shipping routes to identify vulnerable transit bottlenecks."
            ),
            ChainOfIntelligenceStep(
                step_number=5,
                stage_name="5. WHAT HAPPENS TO CASH & CARBON",
                headline=f"${wc_state.transit_inventory_cash_lockup_usd_millions}M Trapped Cash Lockup & +{c_state.route_diversion_co2_penalty_pct}% Scope 3 Carbon Surge",
                data_summary=f"Transit delays extend Cash Conversion Cycles (+{wc_state.cash_conversion_cycle_expansion_days} days) while rerouted voyages generate {c_state.daily_regional_freight_co2_tonnes} tonnes of CO2e daily.",
                key_metrics={
                    "cash_lockup_usd_m": wc_state.transit_inventory_cash_lockup_usd_millions,
                    "ccc_expansion_days": wc_state.cash_conversion_cycle_expansion_days,
                    "daily_co2_tonnes": c_state.daily_regional_freight_co2_tonnes,
                    "co2_penalty_pct": c_state.route_diversion_co2_penalty_pct,
                },
                actionable_insight="Quantify Scope 3 carbon tax penalties (EU CBAM / SG Carbon Tax) and optimize working capital financing."
            ),
            ChainOfIntelligenceStep(
                step_number=6,
                stage_name="6. WHAT MANAGEMENT SHOULD INVESTIGATE",
                headline="Execute Strategic Countermeasures: Activate SCF Facilities & Hedge Gasoil Spreads",
                data_summary="C-suite & risk managers should activate pre-approved Supply Chain Finance ($1.2B gap) to relieve liquidity stress, hedge middle distillate crack spreads, and re-allocate regional safety stocks.",
                key_metrics={
                    "scf_liquidity_gap_usd_m": wc_state.scf_liquidity_gap_usd_millions,
                    "carrying_cost_penalty_usd_m": wc_state.inventory_carrying_cost_penalty_monthly_usd_millions,
                },
                actionable_insight="Convene supply chain & treasury executive committee to execute liquidity buffer drawing and multi-modal freight rerouting."
            )
        ]

        return ChainOfIntelligenceCascade(
            timestamp=datetime.now(timezone.utc).isoformat(),
            focus_topic="ASEAN Trade, Energy & Supply Chain Intelligence Cascade",
            steps=steps
        )


chain_of_intelligence = ChainOfIntelligenceSynthesizer()
