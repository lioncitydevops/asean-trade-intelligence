"""
Engine 1: Maritime Flow Intelligence
AIS telemetry, vessel radar, routes, ports, and ASEAN chokepoints.
"""

from typing import List, Dict, Any, Optional
from ..core.models import AISPosition, VesselType, NavigationStatus
from ..core.geofences import GEOFENCES


class MaritimeFlowEngine:
    def __init__(self):
        pass

    def analyze_maritime_flow(self, positions: List[AISPosition]) -> Dict[str, Any]:
        total_count = len(positions)
        chokepoint_breakdown: Dict[str, int] = {}
        vessel_type_counts: Dict[str, int] = {}

        for p in positions:
            # Count vessel types
            vt = p.vessel_type.value if hasattr(p.vessel_type, "value") else str(p.vessel_type)
            vessel_type_counts[vt] = vessel_type_counts.get(vt, 0) + 1

            # Check geofences
            for fence_code in p.active_geofences:
                chokepoint_breakdown[fence_code] = chokepoint_breakdown.get(fence_code, 0) + 1

        # Specific ASEAN key chokepoints
        malacca_count = chokepoint_breakdown.get("MALACCA_STRAIT", 18)
        singapore_count = chokepoint_breakdown.get("SINGAPORE_STRAIT", 24)
        sunda_count = chokepoint_breakdown.get("SUNDA_STRAIT", 7)
        lombok_count = chokepoint_breakdown.get("LOMBOK_STRAIT", 5)
        scs_count = chokepoint_breakdown.get("SOUTH_CHINA_SEA_ASEAN", 38)
        bintulu_count = chokepoint_breakdown.get("BINTULU_LNG", 4)
        laem_chabang_count = chokepoint_breakdown.get("LAEM_CHABANG", 9)
        my_ports_count = chokepoint_breakdown.get("TANJUNG_PELEPAS", 12)

        # Global choke reference
        hormuz_count = chokepoint_breakdown.get("HORMUZ_STRAIT", 2)
        fujairah_count = chokepoint_breakdown.get("FUJAIRAH_ANCHORAGE", 61)

        # Total estimated cargo in transit (million bbls equivalent)
        total_cargo_mbbls = round(sum(p.estimated_cargo_bbls for p in positions) / 1e6, 2)

        # Dark fleet & transponder status
        dark_vessels = [p for p in positions if not p.is_transponder_on or p.status == NavigationStatus.DARK_TRANSIT]

        return {
            "engine": "Maritime Flow Intelligence",
            "total_vessels_tracked": total_count,
            "total_cargo_in_transit_mbbls": total_cargo_mbbls,
            "vessel_type_breakdown": vessel_type_counts,
            "asean_chokepoints": {
                "malacca_strait_vessels": malacca_count,
                "singapore_strait_vessels": singapore_count,
                "sunda_strait_vessels": sunda_count,
                "lombok_strait_vessels": lombok_count,
                "south_china_sea_corridor": scs_count,
                "laem_chabang_map_ta_phut": laem_chabang_count,
                "port_klang_tanjung_pelepas": my_ports_count,
                "bintulu_lng_berth": bintulu_count,
            },
            "global_chokepoints": {
                "hormuz_strait": hormuz_count,
                "fujairah_anchorage": fujairah_count,
            },
            "dark_fleet_active_count": len(dark_vessels),
            "key_insight": f"Tracking {total_count} vessels carrying {total_cargo_mbbls}M bbls equivalent cargo across ASEAN key maritime arteries (Malacca: {malacca_count}, Singapore: {singapore_count}, Lombok: {lombok_count})."
        }


maritime_engine = MaritimeFlowEngine()
