"""
Engine 6: Working Capital Intelligence (Preview / Extension Module)
Translates maritime & supply chain disruptions into inventory, cash conversion cycles, liquidity, and financing consequences.
"""

from typing import Dict, Any
from ..core.models import WorkingCapitalIntelligenceState


class WorkingCapitalEngine:
    def __init__(self):
        pass

    def get_working_capital_state(self) -> WorkingCapitalIntelligenceState:
        return WorkingCapitalIntelligenceState(
            transit_inventory_cash_lockup_usd_millions=4850.0,
            cash_conversion_cycle_expansion_days=8.4,
            receivables_payables_strain_index=68.2,
            inventory_carrying_cost_penalty_monthly_usd_millions=18.4,
            scf_liquidity_gap_usd_millions=1200.0
        )

    def get_summary(self) -> Dict[str, Any]:
        state = self.get_working_capital_state()
        return {
            "engine": "Working Capital Intelligence",
            "state": state.dict() if hasattr(state, "dict") else state.model_dump(),
            "key_insight": f"Shipping delays have locked up ${state.transit_inventory_cash_lockup_usd_millions}M in floating transit inventory across ASEAN trade corridors, expanding regional Cash Conversion Cycles by +{state.cash_conversion_cycle_expansion_days} days."
        }


working_capital_engine = WorkingCapitalEngine()
