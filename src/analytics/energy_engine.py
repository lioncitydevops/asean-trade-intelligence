"""
Engine 2: Energy Intelligence
Crude benchmarks, refined petroleum products, LNG, bio-fuels, crack spreads, and ASEAN energy storage.
"""

from typing import Dict, Any
from ..core.models import EnergyIntelligenceState
from ..data.market_feed import get_market_intelligence


class EnergyIntelligenceEngine:
    def __init__(self):
        pass

    def get_energy_state(self) -> EnergyIntelligenceState:
        mkt = get_market_intelligence()
        brent = mkt.get("brent_prompt_price", 104.50)
        wti = mkt.get("wti_prompt_price", 99.80)

        # ASEAN Crude & Product Pricing Calibration
        dubai = round(brent - 2.70, 2)
        tapis = round(brent + 3.70, 2)  # Tapis premium ASEAN sweet crude benchmark
        gasoil_crack = round(28.50 + (brent - 104.50) * 0.15, 2)  # SG Gasoil 10ppm crack spread $/bbl
        gasoline_crack = round(18.20 + (brent - 104.50) * 0.10, 2)  # RON95 Gasoline crack spread $/bbl
        jet_crack = round(26.40 + (brent - 104.50) * 0.12, 2)       # Jet Fuel A-1 crack spread $/bbl
        jkm_lng = round(14.80 + (brent - 104.50) * 0.08, 2)         # JKM Spot LNG $/MMBtu

        sg_stocks = 24.8  # Million bbls commercial onshore oil stocks in Singapore
        floating_storage = 18.2 # Million bbls Fujairah & ASEAN floating crude storage

        return EnergyIntelligenceState(
            brent_prompt_usd=brent,
            dubai_crude_usd=dubai,
            tapis_asean_usd=tapis,
            wti_crude_usd=wti,
            singapore_gasoil_crack_usd=gasoil_crack,
            gasoline_ron95_crack_usd=gasoline_crack,
            jet_fuel_crack_usd=jet_crack,
            jkm_spot_lng_usd=jkm_lng,
            singapore_onshore_stocks_mbbls=sg_stocks,
            fujairah_asean_floating_storage_mbbls=floating_storage,
            curve_structure=mkt.get("forward_curve_structure", "Inverted / Steep Backwardation")
        )

    def get_summary(self) -> Dict[str, Any]:
        state = self.get_energy_state()
        return {
            "engine": "Energy Intelligence",
            "state": state.dict() if hasattr(state, "dict") else state.model_dump(),
            "key_insight": f"Brent at ${state.brent_prompt_usd}/bbl; Tapis ASEAN sweet crude premium at ${state.tapis_asean_usd}/bbl. Singapore Gasoil crack spread remains elevated at ${state.singapore_gasoil_crack_usd}/bbl reflecting middle distillate tightness."
        }


energy_engine = EnergyIntelligenceEngine()
