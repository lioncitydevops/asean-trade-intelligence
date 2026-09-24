"""
Engine 3: Supply Chain Risk Intelligence
Disruptions, rerouting, congestion, bottleneck risk scores, and sector exposure.
"""

from typing import Dict, Any, List
from ..core.models import SupplyChainRiskState


class SupplyChainRiskEngine:
    def __init__(self):
        pass

    def get_risk_state(self) -> SupplyChainRiskState:
        top_sectors = [
            {
                "sector": "Semiconductors & Electronics Assembly",
                "hubs": ["Penang (MY)", "Singapore Hub", "Northern Vietnam"],
                "exposure_score": 88.5,
                "bottleneck_factor": "Container berth dwell times in Singapore + air freight capacity squeeze.",
                "action": "Increase safety stock buffers by +14 days; evaluate Sunda feeder routes."
            },
            {
                "sector": "Refining & Petrochemical Feedstocks",
                "hubs": ["Map Ta Phut (TH)", "Jurong Island (SG)", "Kertih / PTT (MY/TH)"],
                "exposure_score": 82.0,
                "bottleneck_factor": "Malacca Strait draft limitations on laden VLCC crude deliveries.",
                "action": "Lightering via Fujairah STS or deepwater Lombok bypass for heavy crude."
            },
            {
                "sector": "Automotive & Heavy Manufacturing",
                "hubs": ["Eastern Seaboard (TH)", "West Java (ID)", "Klang Valley (MY)"],
                "exposure_score": 74.2,
                "bottleneck_factor": "Component shipment delays from European suppliers bypassing Red Sea.",
                "action": "Dual-sourcing component supply from regional ASEAN aggregators."
            },
            {
                "sector": "Power Generation & Utilities",
                "hubs": ["EGAT (TH)", "Tenaga Nasional (MY)", "PLN (ID)"],
                "exposure_score": 69.0,
                "bottleneck_factor": "LNG spot price spikes (JKM) and LNG carrier queueing at berths.",
                "action": "Optimize long-term pipeline gas contracts with Petronas Bintulu stream."
            }
        ]

        return SupplyChainRiskState(
            malacca_bottleneck_risk_score=78.5,
            south_china_sea_hazard_index=64.0,
            cape_diversion_delay_days=12.4,
            singapore_container_dwell_days=3.4,
            port_klang_anchorage_wait_hours=42.0,
            top_exposed_sectors=top_sectors
        )

    def get_summary(self) -> Dict[str, Any]:
        state = self.get_risk_state()
        return {
            "engine": "Supply Chain Risk Intelligence",
            "state": state.dict() if hasattr(state, "dict") else state.model_dump(),
            "key_insight": f"Malacca Strait Risk Score stands at {state.malacca_bottleneck_risk_score}/100. Cape of Good Hope rerouting adds +{state.cape_diversion_delay_days} days to Europe-ASEAN transit times, driving Singapore container berth dwell times to {state.singapore_container_dwell_days} days."
        }


supply_chain_engine = SupplyChainRiskEngine()
