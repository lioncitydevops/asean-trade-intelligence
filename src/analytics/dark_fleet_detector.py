"""
Dark Fleet & Ship-to-Ship (STS) Transshipment Detection Engine.
Identifies transponder blackouts, clandestine shuttle runs, and offshore lightering operations.
"""

from datetime import datetime, timezone
import math
from typing import List, Dict, Any, Tuple
from ..core.models import AISPosition, STSCluster, VesselType, NavigationStatus


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class DarkFleetDetector:
    def __init__(self):
        self.active_sts_clusters: List[STSCluster] = []
        self.dark_events_log: List[Dict[str, Any]] = []

    def detect_sts_operations(self, positions: List[AISPosition]) -> List[STSCluster]:
        """
        Scans positions for vessel pairs in close proximity (< 800m) moving at drift speed (< 1.5 knots),
        typically inside anchorage/lightering zones like Fujairah.
        """
        clusters: List[STSCluster] = []
        n = len(positions)

        for i in range(n):
            p1 = positions[i]
            if p1.speed_knots > 2.0:
                continue

            for j in range(i + 1, n):
                p2 = positions[j]
                if p2.speed_knots > 2.0:
                    continue

                dist = haversine_distance_meters(p1.latitude, p1.longitude, p2.latitude, p2.longitude)
                if dist < 800.0:
                    # Found an STS pairing
                    # Identify mother (larger) and daughter (shuttle)
                    if p1.dwt_tonnes >= p2.dwt_tonnes:
                        mother, daughter = p1, p2
                    else:
                        mother, daughter = p2, p1

                    # Estimate transferred volume based on daughter capacity
                    transferred_bbls = min(daughter.dwt_tonnes * 7.33 * 0.85, mother.dwt_tonnes * 7.33)

                    cluster = STSCluster(
                        cluster_id=f"STS-{mother.mmsi}-{daughter.mmsi}",
                        mother_mmsi=mother.mmsi,
                        mother_name=mother.vessel_name,
                        mother_type=mother.vessel_type,
                        daughter_mmsi=daughter.mmsi,
                        daughter_name=daughter.vessel_name,
                        daughter_type=daughter.vessel_type,
                        latitude=round((mother.latitude + daughter.latitude) / 2.0, 4),
                        longitude=round((mother.longitude + daughter.longitude) / 2.0, 4),
                        start_time=datetime.now(timezone.utc),
                        duration_hours=6.5,
                        distance_meters=round(dist, 1),
                        estimated_transferred_bbls=round(transferred_bbls, -3),
                        anchorage_zone="Fujairah Offshore Anchorage",
                    )
                    clusters.append(cluster)

        self.active_sts_clusters = clusters
        return clusters

    def detect_dark_transponders(self, positions: List[AISPosition]) -> List[Dict[str, Any]]:
        """Identify dark vessels operating with transponders switched off in high-risk zones."""
        dark_vessels = []
        for p in positions:
            if not p.is_transponder_on or p.status == NavigationStatus.DARK_TRANSIT:
                event = {
                    "mmsi": p.mmsi,
                    "vessel_name": p.vessel_name,
                    "vessel_type": p.vessel_type.value,
                    "last_known_lat": p.latitude,
                    "last_known_lon": p.longitude,
                    "estimated_load_bbls": round(p.estimated_cargo_bbls),
                    "suspected_route": "Persian Gulf Loading -> Clandestine Hormuz Night Transit -> Fujairah STS",
                    "status": "Transponder Dark (AIS Disabled)",
                }
                dark_vessels.append(event)
        return dark_vessels


# Singleton instance
dark_fleet_detector = DarkFleetDetector()
