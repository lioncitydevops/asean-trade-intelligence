"""
Core data models and schemas for Maritime Oil Flow Intelligence & Real-Time Reporting.
"""

from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VesselType(str, Enum):
    VLCC = "VLCC"                     # ~2,000,000 bbls / 300,000 DWT
    SUEZMAX = "Suezmax"               # ~1,000,000 bbls / 160,000 DWT
    AFRAMAX = "Aframax"               # ~750,000 bbls / 115,000 DWT
    PANAMAX = "Panamax"               # ~500,000 bbls / 75,000 DWT
    SHUTTLE_TANKER = "Shuttle Tanker" # ~300,000 - 600,000 bbls (Clandestine transit)
    PRODUCT_TANKER = "Product Tanker" # ~300,000 bbls
    BUNKER_TANKER = "Bunker Tanker"   # Refueling services
    LNG_CARRIER = "LNG Carrier"       # ~170,000 m3 LNG (~3.8 Bcf gas)
    CONTAINER_SHIP = "Container Ship" # ~14,000 TEU
    BULK_CARRIER = "Bulk Carrier"     # ~180,000 DWT Iron Ore/Coal


class NavigationStatus(str, Enum):
    UNDERWAY = "Underway"
    ANCHORED = "Anchored"
    MOORED = "Moored"
    STS_TRANSFER = "Ship-to-Ship Transfer"
    DARK_TRANSIT = "Dark / AIS Disabled"


class AISPosition(BaseModel):
    mmsi: int
    imo: Optional[int] = None
    vessel_name: str
    vessel_type: VesselType
    latitude: float
    longitude: float
    speed_knots: float
    heading_deg: float
    draught_m: float
    max_draught_m: float
    dwt_tonnes: float
    destination: str
    is_transponder_on: bool = True
    status: NavigationStatus = NavigationStatus.UNDERWAY
    timestamp: datetime
    active_geofences: List[str] = Field(default_factory=list)

    @property
    def estimated_cargo_bbls(self) -> float:
        """Estimate crude/product load based on current draught vs max draught and DWT."""
        if self.max_draught_m <= 0:
            return 0.0
        load_ratio = max(0.0, min(1.0, (self.draught_m - 6.0) / max(1.0, self.max_draught_m - 6.0)))
        if self.vessel_type in [VesselType.VLCC, VesselType.SUEZMAX, VesselType.AFRAMAX, VesselType.SHUTTLE_TANKER]:
            return self.dwt_tonnes * 7.33 * load_ratio
        elif self.vessel_type == VesselType.PRODUCT_TANKER:
            return self.dwt_tonnes * 7.55 * load_ratio
        elif self.vessel_type == VesselType.LNG_CARRIER:
            return self.dwt_tonnes * 9.2 * load_ratio # Equivalent bbls
        return self.dwt_tonnes * 5.0 * load_ratio


class ChokepointTransit(BaseModel):
    transit_id: str
    chokepoint: str  # e.g., "Malacca Strait", "Singapore Strait", "Hormuz", "Bab El-Mandeb", "Suez Canal"
    mmsi: int
    vessel_name: str
    vessel_type: VesselType
    direction: str   # "Outbound", "Inbound", "Northbound", "Southbound"
    timestamp: datetime
    estimated_cargo_bbls: float
    is_dark: bool = False
    details: Optional[str] = None


class STSCluster(BaseModel):
    cluster_id: str
    mother_mmsi: int
    mother_name: str
    mother_type: VesselType
    daughter_mmsi: int
    daughter_name: str
    daughter_type: VesselType
    latitude: float
    longitude: float
    start_time: datetime
    duration_hours: float
    distance_meters: float
    estimated_transferred_bbls: float
    anchorage_zone: str = "Singapore / Fujairah Offshore"


class DailyChokepointMetric(BaseModel):
    date_str: str
    chokepoint: str
    daily_count: int
    capacity_million_bbls: float
    seven_day_ma: float
    historical_min: float
    historical_max: float
    historical_avg: float


class DailyDemandMetric(BaseModel):
    date_str: str
    country: str
    daily_imports_million_bbls: float
    thirty_day_ma: float
    rebased_index: float  # Base 100 = 2026-02-28


class EnergyIntelligenceState(BaseModel):
    brent_prompt_usd: float
    dubai_crude_usd: float
    tapis_asean_usd: float
    wti_crude_usd: float
    singapore_gasoil_crack_usd: float
    gasoline_ron95_crack_usd: float
    jet_fuel_crack_usd: float
    jkm_spot_lng_usd: float
    singapore_onshore_stocks_mbbls: float
    fujairah_asean_floating_storage_mbbls: float
    curve_structure: str


class SupplyChainRiskState(BaseModel):
    malacca_bottleneck_risk_score: float  # 0 - 100
    south_china_sea_hazard_index: float  # 0 - 100
    cape_diversion_delay_days: float     # e.g. +12.4 days
    singapore_container_dwell_days: float
    port_klang_anchorage_wait_hours: float
    top_exposed_sectors: List[Dict[str, Any]]


class MacroNowcastState(BaseModel):
    asean_maritime_trade_volume_index: float  # Base 100
    amtvi_yoy_pct: float
    industrial_input_velocity_index: float
    asean_pmi_nowcast: float
    gdp_nowcast_impact: Dict[str, float]  # SG, MY, TH, ID, VN, PH


class CarbonIntelligenceState(BaseModel):
    daily_regional_freight_co2_tonnes: float
    route_diversion_co2_penalty_pct: float
    total_tonne_km_daily_billions: float
    cii_rating_distribution_pct: Dict[str, float]  # A, B, C, D, E
    cbam_carbon_tax_liability_usd_tonne: float


class WorkingCapitalIntelligenceState(BaseModel):
    transit_inventory_cash_lockup_usd_millions: float
    cash_conversion_cycle_expansion_days: float
    receivables_payables_strain_index: float  # 0 - 100
    inventory_carrying_cost_penalty_monthly_usd_millions: float
    scf_liquidity_gap_usd_millions: float


class ChainOfIntelligenceStep(BaseModel):
    step_number: int
    stage_name: str
    headline: str
    data_summary: str
    key_metrics: Dict[str, Any]
    actionable_insight: str


class ChainOfIntelligenceCascade(BaseModel):
    timestamp: str
    focus_topic: str
    steps: List[ChainOfIntelligenceStep]


class MacroInsightsSummary(BaseModel):
    edition_date: str
    title: str
    subtitle: str
    crude_futures_price: float
    curve_structure: str
    hormuz_active_vessels_today: int
    hormuz_active_capacity_mbbls: float
    hormuz_baseline_vessels: int
    hormuz_baseline_capacity_mbbls: float
    hormuz_dark_crossings_today: int
    fujairah_anchored_tankers: int
    fujairah_anchored_capacity_mbbls: float
    fujairah_turnover_outflow_pct: float
    bab_el_mandeb_7day_ma: float
    suez_canal_7day_ma: float
    petroline_status: str
    yanbu_daily_outflow_mbbls: float
    china_demand_reduction_pct: float
    india_demand_index: float
    japan_demand_index: float
    skorea_demand_index: float
    energy_intel: EnergyIntelligenceState
    risk_intel: SupplyChainRiskState
    macro_nowcast: MacroNowcastState
    carbon_intel: CarbonIntelligenceState
    working_capital_intel: WorkingCapitalIntelligenceState
    chain_of_intel: ChainOfIntelligenceCascade
    executive_summary_paragraphs: List[str]
    sections: Dict[str, Any]

