"""
Real-Time AIS Stream Simulator & Maritime Fleet Telemetry Engine.
Simulates realistic global crude tanker movements, dark-fleet AIS dropouts,
and offshore ship-to-ship lightering operations.
"""

import math
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from ..core.models import AISPosition, VesselType, NavigationStatus
from ..core.geofences import check_active_geofences, GEOFENCES


# Named realistic ASEAN & global maritime fleet
SAMPLE_VESSELS = [
    # VLCCs (2M barrels capacity)
    {"name": "APOLLO STAR", "type": VesselType.VLCC, "dwt": 310000, "draught": 21.5, "max_d": 22.5, "mmsi": 412001001, "route": "GULF_TO_CHINA"},
    {"name": "OCEAN GLORY", "type": VesselType.VLCC, "dwt": 305000, "draught": 20.8, "max_d": 22.0, "mmsi": 412001002, "route": "MALACCA_SINGAPORE"},
    {"name": "TITAN DISCOVERY", "type": VesselType.VLCC, "dwt": 318000, "draught": 21.9, "max_d": 22.8, "mmsi": 412001003, "route": "LOMBOK_DEEPWATER"},
    {"name": "SEA HARMONY", "type": VesselType.VLCC, "dwt": 298000, "draught": 20.2, "max_d": 21.5, "mmsi": 412001004, "route": "FUJAIRAH_TO_KOREA"},
    {"name": "PACIFIC SPLENDOR", "type": VesselType.VLCC, "dwt": 320000, "draught": 22.0, "max_d": 23.0, "mmsi": 412001005, "route": "GULF_TO_CHINA"},
    
    # LNG Carriers & Product Tankers
    {"name": "PETRONAS BINTULU I", "type": VesselType.LNG_CARRIER, "dwt": 95000, "draught": 11.2, "max_d": 12.5, "mmsi": 538006001, "route": "BINTULU_TO_SINGAPORE"},
    {"name": "SARAWAK GAS EXPLORER", "type": VesselType.LNG_CARRIER, "dwt": 98000, "draught": 11.5, "max_d": 12.8, "mmsi": 538006002, "route": "BINTULU_TO_SINGAPORE"},
    {"name": "SINGAPORE MARINER", "type": VesselType.PRODUCT_TANKER, "dwt": 48000, "draught": 10.2, "max_d": 11.8, "mmsi": 538007001, "route": "MALACCA_SINGAPORE"},
    {"name": "JURONG PHOENIX", "type": VesselType.PRODUCT_TANKER, "dwt": 52000, "draught": 10.6, "max_d": 12.0, "mmsi": 538007002, "route": "LAEM_CHABANG_SCS"},

    # Container & Bulk Carriers
    {"name": "MAERSK MALACCA", "type": VesselType.CONTAINER_SHIP, "dwt": 165000, "draught": 15.5, "max_d": 16.5, "mmsi": 538008001, "route": "MALACCA_SINGAPORE"},
    {"name": "EVERGREEN SUNDA", "type": VesselType.CONTAINER_SHIP, "dwt": 155000, "draught": 14.8, "max_d": 16.0, "mmsi": 538008002, "route": "SUNDA_CORRIDOR"},
    {"name": "INDONESIA BULKER", "type": VesselType.BULK_CARRIER, "dwt": 180000, "draught": 17.5, "max_d": 18.2, "mmsi": 538009001, "route": "SUNDA_CORRIDOR"},

    # Suezmaxes & Aframaxes
    {"name": "ARABIAN RUNNER", "type": VesselType.SUEZMAX, "dwt": 158000, "draught": 16.5, "max_d": 17.2, "mmsi": 413002001, "route": "MALACCA_SINGAPORE"},
    {"name": "RED SEA EXPLORER", "type": VesselType.SUEZMAX, "dwt": 160000, "draught": 16.8, "max_d": 17.5, "mmsi": 413002002, "route": "RED_SEA_SUEZ"},
    {"name": "DESERT CROWN", "type": VesselType.SUEZMAX, "dwt": 156000, "draught": 15.9, "max_d": 17.0, "mmsi": 413002003, "route": "FUJAIRAH_STS_MOTHER"},
    {"name": "GULF VOYAGER", "type": VesselType.AFRAMAX, "dwt": 115000, "draught": 14.2, "max_d": 15.0, "mmsi": 414003001, "route": "LAEM_CHABANG_SCS"},
    {"name": "ASIAN MERCURY", "type": VesselType.AFRAMAX, "dwt": 118000, "draught": 14.5, "max_d": 15.2, "mmsi": 414003003, "route": "CHINA_COASTAL"},

    # Clandestine Shuttle Tankers & Bunkers
    {"name": "SHUTTLE FALCON I", "type": VesselType.SHUTTLE_TANKER, "dwt": 45000, "draught": 10.5, "max_d": 11.5, "mmsi": 415004001, "route": "HORMUZ_SHUTTLE_DARK"},
    {"name": "FUJAIRAH FUELER I", "type": VesselType.BUNKER_TANKER, "dwt": 12000, "draught": 6.5, "max_d": 7.5, "mmsi": 416005001, "route": "FUJAIRAH_BUNKER"},
]

# Strategic Route Waypoints
ROUTE_WAYPOINTS = {
    "MALACCA_SINGAPORE": [
        (5.5, 97.5),   # Northern Malacca
        (3.5, 100.5),  # Mid Malacca
        (1.3, 103.8),  # Singapore Strait
        (3.0, 105.5),  # South China Sea Entry
    ],
    "BINTULU_TO_SINGAPORE": [
        (3.2, 113.0),  # Bintulu Sarawak
        (2.5, 108.5),  # South China Sea Mid
        (1.3, 104.0),  # Singapore Terminal
    ],
    "SUNDA_CORRIDOR": [
        (-8.0, 105.0), # Indian Ocean South
        (-5.9, 105.8), # Sunda Strait
        (-3.0, 108.0), # Java Sea / South China Sea
    ],
    "LOMBOK_DEEPWATER": [
        (-10.0, 115.5),# Indian Ocean South
        (-8.5, 115.8), # Lombok Strait
        (-4.0, 117.5), # Makassar Strait
        (5.0, 119.0),  # Celebes Sea
    ],
    "LAEM_CHABANG_SCS": [
        (12.8, 100.9), # Gulf of Thailand
        (9.0, 104.5),  # Southern Vietnam
        (4.0, 108.0),  # SCS Lane
        (1.3, 103.9),  # Singapore Hub
    ],
    "GULF_TO_CHINA": [
        (26.8, 50.2),  # Ras Tanura
        (26.0, 56.7),  # Hormuz Outflow
        (20.0, 65.0),  # Arabian Sea
        (06.0, 80.0),  # Sri Lanka south
        (02.5, 101.5), # Malacca
        (30.0, 122.5), # Zhoushan China
    ],
    "FUJAIRAH_TO_JAPAN": [
        (25.2, 56.5),  # Fujairah Anchorage
        (05.5, 80.5),  # South of Sri Lanka
        (03.0, 102.0), # Malacca Strait
        (15.0, 118.0), # South China Sea
        (35.0, 139.8), # Tokyo Bay Japan
    ],
    "FUJAIRAH_TO_KOREA": [
        (25.2, 56.5),  # Fujairah Anchorage
        (02.5, 102.0), # Malacca Strait
        (22.0, 120.0), # Taiwan Strait
        (35.5, 129.4), # Ulsan Korea
    ],
    "RED_SEA_SUEZ": [
        (12.6, 43.4),  # Bab El-Mandeb
        (20.0, 39.0),  # Red Sea Mid
        (27.8, 33.8),  # Gulf of Suez
        (29.9, 32.5),  # Suez Canal Entry
    ],
    "FUJAIRAH_STS_MOTHER": [
        (25.22, 56.50), # Anchored in Fujairah STS zone
        (25.23, 56.51),
        (25.21, 56.49),
    ],
    "HORMUZ_SHUTTLE_DARK": [
        (27.2, 51.5),  # Loading Gulf side (Iran/PG)
        (26.4, 55.8),  # Hormuz (Dark at night)
        (25.22, 56.50),# Fujairah STS Rendezvous
    ],
    "FUJAIRAH_BUNKER": [
        (25.18, 56.45),
        (25.30, 56.58),
        (25.15, 56.42),
    ],
    "CHINA_COASTAL": [
        (22.0, 114.0),
        (30.0, 122.5),
        (36.0, 120.5),
    ]
}


class AISStreamEngine:
    def __init__(self):
        self.vessels_state: List[Dict] = []
        self._init_fleet()

    def _init_fleet(self):
        """Initialize fleet with varied initial progress and positions along routes."""
        for v in SAMPLE_VESSELS:
            route_name = v["route"]
            waypoints = ROUTE_WAYPOINTS.get(route_name, [(25.2, 56.5)])
            progress = random.uniform(0.0, 0.95)
            
            # Additional fleet replication for scale (multiply fleet to ~120 vessels)
            for copy_idx in range(5):
                mmsi = v["mmsi"] + (copy_idx * 10000)
                v_copy = {
                    "mmsi": mmsi,
                    "imo": 9000000 + (mmsi % 900000),
                    "name": f"{v['name']} {'IV' if copy_idx==3 else 'III' if copy_idx==2 else 'II' if copy_idx==1 else ''}".strip(),
                    "type": v["type"],
                    "dwt": v["dwt"],
                    "draught": v["draught"],
                    "max_draught": v["max_d"],
                    "route": route_name,
                    "waypoints": waypoints,
                    "progress": (progress + copy_idx * 0.18) % 1.0,
                    "speed": random.uniform(11.5, 14.5) if v["type"] != VesselType.BUNKER_TANKER else random.uniform(4.0, 8.0),
                    "is_dark": "DARK" in route_name,
                    "last_update": datetime.now(timezone.utc),
                }
                self.vessels_state.append(v_copy)

    def step_simulation(self, delta_minutes: float = 15.0) -> List[AISPosition]:
        """Advance vessel positions along their routes and emit AIS messages."""
        now = datetime.now(timezone.utc)
        current_positions: List[AISPosition] = []

        for v in self.vessels_state:
            waypoints = v["waypoints"]
            n_pts = len(waypoints)
            
            if n_pts == 1:
                # Stationary/anchored
                lat, lon = waypoints[0]
                speed = 0.1
                heading = random.uniform(0, 360)
                status = NavigationStatus.ANCHORED
            else:
                # Move along waypoints
                speed = v["speed"]
                dist_traveled_deg = (speed * (delta_minutes / 60.0)) / 60.0  # Approx nautical miles to deg
                total_segs = n_pts - 1
                curr_seg_idx = min(int(v["progress"] * total_segs), total_segs - 1)
                seg_progress = (v["progress"] * total_segs) - curr_seg_idx

                p1 = waypoints[curr_seg_idx]
                p2 = waypoints[curr_seg_idx + 1]

                lat = p1[0] + (p2[0] - p1[0]) * seg_progress + random.uniform(-0.02, 0.02)
                lon = p1[1] + (p2[1] - p1[1]) * seg_progress + random.uniform(-0.02, 0.02)

                # Compute heading
                d_lat = p2[0] - p1[0]
                d_lon = p2[1] - p1[1]
                heading = (math.degrees(math.atan2(d_lon, d_lat)) + 360) % 360

                # Advance progress
                v["progress"] = (v["progress"] + 0.005 * (delta_minutes / 15.0)) % 1.0

                # Check if anchored at Fujairah or in STS
                if "STS" in v["route"] or "BUNKER" in v["route"]:
                    status = NavigationStatus.STS_TRANSFER if "STS" in v["route"] else NavigationStatus.ANCHORED
                    speed = 0.2
                elif v["is_dark"] and (25.5 <= lat <= 27.0 and 55.0 <= lon <= 57.0):
                    status = NavigationStatus.DARK_TRANSIT
                else:
                    status = NavigationStatus.UNDERWAY

            # Transponder state
            is_transponder_on = True
            if status == NavigationStatus.DARK_TRANSIT:
                is_transponder_on = False

            active_fences = check_active_geofences(lat, lon)

            # Determine destination string
            dest = "FUJAIRAH STS" if "STS" in v["route"] else "CHINA ZHOUSHAN" if "CHINA" in v["route"] else "INDIA SIKKA" if "INDIA" in v["route"] else "RED SEA/SUEZ"

            pos = AISPosition(
                mmsi=v["mmsi"],
                imo=v["imo"],
                vessel_name=v["name"],
                vessel_type=v["type"],
                latitude=round(lat, 4),
                longitude=round(lon, 4),
                speed_knots=round(speed, 1),
                heading_deg=round(heading, 1),
                draught_m=v["draught"],
                max_draught_m=v["max_draught"],
                dwt_tonnes=v["dwt"],
                destination=dest,
                is_transponder_on=is_transponder_on,
                status=status,
                timestamp=now,
                active_geofences=active_fences,
            )
            current_positions.append(pos)

        return current_positions


# Singleton instance
stream_engine = AISStreamEngine()
