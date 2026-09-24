"""
Spatial geofencing and maritime transit detection geometries for key oil chokepoints.
"""

from typing import List, Tuple, Dict, Any


class Point:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon


class GeofencePolygon:
    def __init__(self, name: str, code: str, polygon: List[Tuple[float, float]], description: str = ""):
        self.name = name
        self.code = code
        self.polygon = polygon  # List of (lat, lon) tuples
        self.description = description

    def contains(self, lat: float, lon: float) -> bool:
        """Ray-casting algorithm for point-in-polygon containment."""
        n = len(self.polygon)
        inside = False
        p1_lat, p1_lon = self.polygon[0]
        for i in range(1, n + 1):
            p2_lat, p2_lon = self.polygon[i % n]
            if lon > min(p1_lon, p2_lon):
                if lon <= max(p1_lon, p2_lon):
                    if lat <= max(p1_lat, p2_lat):
                        if p1_lon != p2_lon:
                            lat_inters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                            if p1_lat == p2_lat or lat <= lat_inters:
                                inside = not inside
            p1_lat, p1_lon = p2_lat, p2_lon
        return inside


# Pre-defined strategic geofences for global tanker tracking
GEOFENCES: Dict[str, GeofencePolygon] = {
    "MALACCA_STRAIT": GeofencePolygon(
        name="Strait of Malacca Transit Corridor",
        code="MALACCA",
        polygon=[
            (5.50, 97.50),
            (4.20, 100.20),
            (2.20, 101.80),
            (1.30, 103.30),
            (1.10, 103.60),
            (2.50, 101.20),
            (4.80, 98.20),
        ],
        description="Primary ASEAN maritime artery connecting Indian Ocean to Pacific Ocean trade.",
    ),
    "SINGAPORE_STRAIT": GeofencePolygon(
        name="Singapore Strait & Bunkering Anchorage",
        code="SINGAPORE",
        polygon=[
            (1.45, 103.60),
            (1.45, 104.20),
            (1.10, 104.20),
            (1.10, 103.60),
        ],
        description="Global top bunkering hub, Jurong refining complex, and container transshipment gateway.",
    ),
    "SUNDA_STRAIT": GeofencePolygon(
        name="Sunda Strait (Indonesia)",
        code="SUNDA",
        polygon=[
            (-5.70, 105.40),
            (-5.70, 106.20),
            (-6.20, 106.20),
            (-6.20, 105.40),
        ],
        description="Indonesian maritime passage between Sumatra and Java.",
    ),
    "LOMBOK_STRAIT": GeofencePolygon(
        name="Lombok Strait Deepwater Corridor",
        code="LOMBOK",
        polygon=[
            (-8.20, 115.40),
            (-8.20, 116.20),
            (-8.90, 116.20),
            (-8.90, 115.40),
        ],
        description="Deepwater alternative for fully-laden VLCCs bypassing shallow Malacca Strait.",
    ),
    "SOUTH_CHINA_SEA_ASEAN": GeofencePolygon(
        name="ASEAN South China Sea Trade Lane",
        code="SCS_ASEAN",
        polygon=[
            (18.00, 108.00),
            (18.00, 118.00),
            (5.00, 118.00),
            (5.00, 108.00),
        ],
        description="Crucial ASEAN trade highway carrying $3.4 Trillion in annual seaborne commerce.",
    ),
    "LAEM_CHABANG": GeofencePolygon(
        name="Laem Chabang & Map Ta Phut Hub (Thailand)",
        code="LAEM_CHABANG",
        polygon=[
            (13.20, 100.70),
            (13.20, 101.10),
            (12.40, 101.10),
            (12.40, 100.70),
        ],
        description="Thailand's main deep-sea container terminal and Map Ta Phut petrochemical complex.",
    ),
    "TANJUNG_PELEPAS": GeofencePolygon(
        name="Port Klang & Tanjung Pelepas Hub (Malaysia)",
        code="MY_PORTS",
        polygon=[
            (3.10, 101.20),
            (3.10, 101.50),
            (1.20, 103.60),
            (1.20, 103.30),
        ],
        description="Malaysian primary container transshipment hub and Westports berths.",
    ),
    "BINTULU_LNG": GeofencePolygon(
        name="Bintulu LNG Terminal & Sarawak Corridor (Malaysia)",
        code="BINTULU",
        polygon=[
            (3.50, 112.90),
            (3.50, 113.30),
            (3.10, 113.30),
            (3.10, 112.90),
        ],
        description="Major East Asian LNG export terminal operated by Petronas in Sarawak.",
    ),
    "HORMUZ_STRAIT": GeofencePolygon(
        name="Strait of Hormuz Transit Corridor",
        code="HORMUZ",
        polygon=[
            (26.85, 56.10),
            (26.60, 56.70),
            (26.10, 56.85),
            (25.75, 56.40),
            (25.90, 55.90),
            (26.50, 55.70),
        ],
        description="The primary global crude artery connecting Persian Gulf export terminals to international waters.",
    ),
    "FUJAIRAH_ANCHORAGE": GeofencePolygon(
        name="Fujairah Offshore Anchorage & STS Zone",
        code="FUJAIRAH",
        polygon=[
            (25.40, 56.35),
            (25.40, 56.65),
            (25.00, 56.65),
            (25.00, 56.35),
        ],
        description="UAE primary transshipment, bunkering, and STS lightering anchorage in the Gulf of Oman.",
    ),
    "BAB_EL_MANDEB": GeofencePolygon(
        name="Bab El-Mandeb Strait",
        code="BAB_EL_MANDEB",
        polygon=[
            (13.10, 43.10),
            (13.00, 43.60),
            (12.40, 43.60),
            (12.30, 43.20),
        ],
        description="Southern Red Sea maritime bottleneck controlled by Yemen/Djibouti approaches.",
    ),
    "SUEZ_CANAL": GeofencePolygon(
        name="Suez Canal & SUMED Approach",
        code="SUEZ",
        polygon=[
            (30.10, 32.30),
            (30.10, 32.70),
            (27.60, 34.00),
            (27.40, 33.50),
        ],
        description="Red Sea northern transit gateway connecting Middle East oil to Mediterranean & Europe.",
    ),
    "YANBU_TERMINAL": GeofencePolygon(
        name="Yanbu Petroline Terminal & Port",
        code="YANBU",
        polygon=[
            (24.20, 37.80),
            (24.20, 38.30),
            (23.70, 38.30),
            (23.70, 37.80),
        ],
        description="Saudi western Red Sea crude export terminal at the terminus of the East-West Petroline.",
    ),
    "PERSIAN_GULF_LOADING": GeofencePolygon(
        name="Persian Gulf Terminals (Ras Tanura / Basrah / Mina Al Ahmadi)",
        code="PG_LOAD",
        polygon=[
            (30.10, 48.00),
            (30.10, 52.00),
            (25.00, 54.00),
            (25.00, 48.00),
        ],
        description="Persian Gulf internal waters and major crude loading berths.",
    ),
    "CHINA_DISCHARGE": GeofencePolygon(
        name="China Seaborne Discharge Hubs (Zhoushan / Qingdao)",
        code="CHINA_PORTS",
        polygon=[
            (36.50, 119.50),
            (36.50, 122.50),
            (29.50, 123.00),
            (29.50, 120.00),
        ],
        description="Chinese major coastal refining and crude offloading terminals.",
    ),
    "INDIA_DISCHARGE": GeofencePolygon(
        name="India Seaborne Discharge Hubs (Jamnagar / Vadinar / Sikka)",
        code="INDIA_PORTS",
        polygon=[
            (23.00, 68.50),
            (23.00, 70.50),
            (21.50, 70.50),
            (21.50, 68.50),
        ],
        description="Indian western coast refining and crude offloading terminals in Gulf of Kutch.",
    ),
    "JAPAN_DISCHARGE": GeofencePolygon(
        name="Japan Seaborne Discharge Hubs (Tokyo Bay / Osaka)",
        code="JAPAN_PORTS",
        polygon=[
            (36.00, 139.00),
            (36.00, 140.50),
            (34.00, 140.50),
            (34.00, 139.00),
        ],
        description="Japanese primary crude receiving terminals.",
    ),
    "SKOREA_DISCHARGE": GeofencePolygon(
        name="South Korea Discharge Hubs (Ulsan / Yeosu)",
        code="SKOREA_PORTS",
        polygon=[
            (36.00, 127.00),
            (36.00, 130.00),
            (34.50, 130.00),
            (34.50, 127.00),
        ],
        description="South Korean petrochemical and refining discharge hubs.",
    ),
}


def check_active_geofences(lat: float, lon: float) -> List[str]:
    """Return all geofence codes containing the given coordinate."""
    active = []
    for code, fence in GEOFENCES.items():
        if fence.contains(lat, lon):
            active.append(code)
    return active
