"""
Traffic analysis engine computing chokepoint volume, moving averages, and flow capacity.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from ..core.models import AISPosition, ChokepointTransit, DailyChokepointMetric, NavigationStatus
from ..data.historical_baselines import generate_time_series_data


class TrafficAnalyticsEngine:
    def __init__(self):
        self.raw_data = generate_time_series_data()

    def get_fujairah_series(self) -> pd.DataFrame:
        """Returns the full daily time series for Fujairah anchorage with 7-day MA and 5-year baselines."""
        return self.raw_data["fujairah"]

    def get_redsea_series(self) -> pd.DataFrame:
        """Returns daily series for Bab El-Mandeb and Suez Canal with 7-day MA and 5-year baselines."""
        return self.raw_data["redsea"]

    def get_asian_demand_series(self) -> pd.DataFrame:
        """Returns rebased 30-day MA seaborne import index for China, India, Japan, South Korea."""
        return self.raw_data["asian_demand"]

    def get_current_metrics(self, positions: Optional[List[AISPosition]] = None) -> Dict[str, Any]:
        """Compute latest real-time headline metrics from live fleet positions and baselines."""
        f_df = self.raw_data["fujairah"]
        r_df = self.raw_data["redsea"]
        d_df = self.raw_data["asian_demand"]
        h_df = self.raw_data["hormuz"]

        latest_f = f_df.iloc[-1]
        latest_r = r_df.iloc[-1]
        latest_d = d_df.iloc[-1]
        latest_h = h_df.iloc[-1]

        if positions:
            # 1. Live Hormuz Metrics
            hormuz_vessels = [
                p for p in positions
                if ("HORMUZ_STRAIT" in p.active_geofences or "HORMUZ_SECURITY_ZONE" in p.active_geofences or
                    (25.5 <= p.latitude <= 27.2 and 55.0 <= p.longitude <= 57.2))
            ]
            h_active = [p for p in hormuz_vessels if p.is_transponder_on and p.status != NavigationStatus.DARK_TRANSIT]
            h_dark = [p for p in hormuz_vessels if not p.is_transponder_on or p.status == NavigationStatus.DARK_TRANSIT]

            h_active_count = len(h_active)
            h_dark_count = len(h_dark)
            h_capacity_mbbls = round(sum(p.estimated_cargo_bbls for p in h_active) / 1e6, 2)
            if h_active_count + h_dark_count > 0:
                h_clandestine_pct = round((h_dark_count / (h_active_count + h_dark_count)) * 100, 1)
            else:
                h_clandestine_pct = 85.0

            # 2. Live Fujairah Metrics
            fujairah_vessels = [
                p for p in positions
                if ("FUJAIRAH_ANCHORAGE" in p.active_geofences or "FUJAIRAH_STS_ZONE" in p.active_geofences or
                    (24.8 <= p.latitude <= 25.6 and 56.2 <= p.longitude <= 56.8))
            ]
            f_count = len(fujairah_vessels)
            f_capacity_mbbls = round(sum(p.estimated_cargo_bbls for p in fujairah_vessels) / 1e6, 2)
            f_7d_ma = round(float(latest_f["seven_day_ma"]) + (f_count - float(latest_f["daily_tankers"])) * 0.15, 1)
            f_offset_pct = round(min(80.0, max(20.0, (f_count / max(1, latest_h["active_vessels"] + 1)) * 100.0)), 1)

            # 3. Live Bab el-Mandeb vs Suez
            bem_vessels = [
                p for p in positions
                if ("BAB_EL_MANDEB" in p.active_geofences or (12.0 <= p.latitude <= 14.5 and 42.5 <= p.longitude <= 44.0))
            ]
            suez_vessels = [
                p for p in positions
                if ("SUEZ_CANAL_APPROACH" in p.active_geofences or (27.0 <= p.latitude <= 30.5 and 32.0 <= p.longitude <= 34.5))
            ]
            bem_count = len(bem_vessels)
            suez_count = len(suez_vessels)
            bem_7d_ma = round(float(latest_r["bem_7d_ma"]) + (bem_count - float(latest_r["bem_daily"])) * 0.1, 1)
            suez_7d_ma = round(float(latest_r["suez_7d_ma"]) + (suez_count - float(latest_r["suez_daily"])) * 0.1, 1)

            # 4. Asian Demand Indices
            c_index = round(float(latest_d["china_index"]) - (0.5 if h_active_count < 5 else 0.0), 1)
            i_index = round(float(latest_d["india_index"]) + (0.4 if f_count > 10 else 0.0), 1)
            j_index = round(float(latest_d["japan_index"]), 1)
            sk_index = round(float(latest_d["skorea_index"]), 1)

            return {
                "as_of_date": latest_f["date_str"],
                "hormuz": {
                    "active_vessels_counted": h_active_count,
                    "active_capacity_mbbls": h_capacity_mbbls,
                    "baseline_vessels": 46,
                    "baseline_capacity_mbbls": 19.0,
                    "dark_crossings_estimated": h_dark_count,
                    "clandestine_rate_pct": h_clandestine_pct,
                },
                "fujairah": {
                    "tankers_anchored_today": f_count,
                    "seven_day_ma": f_7d_ma,
                    "historical_5yr_avg": float(latest_f["historical_avg"]),
                    "historical_min": float(latest_f["historical_min"]),
                    "historical_max": float(latest_f["historical_max"]),
                    "turnover_outflow_offset_pct": f_offset_pct,
                    "capacity_mbbls": f_capacity_mbbls,
                },
                "bab_el_mandeb": {
                    "traffic_today": bem_count,
                    "seven_day_ma": bem_7d_ma,
                    "historical_5yr_avg": float(latest_r["bem_avg"]),
                    "trend": "Restricted / Downward",
                },
                "suez_canal": {
                    "traffic_today": suez_count,
                    "seven_day_ma": suez_7d_ma,
                    "historical_5yr_avg": float(latest_r["suez_avg"]),
                    "trend": "Elevated / Diverted Inflow",
                },
                "asian_demand_indices": {
                    "china": c_index,
                    "china_reduction_pct": round(100.0 - c_index, 1),
                    "india": i_index,
                    "japan": j_index,
                    "skorea": sk_index,
                }
            }

        return {
            "as_of_date": latest_f["date_str"],
            "hormuz": {
                "active_vessels_counted": int(latest_h["active_vessels"]),
                "active_capacity_mbbls": round(latest_h["active_vessels"] * 1.0, 1),
                "baseline_vessels": 46,
                "baseline_capacity_mbbls": 19.0,
                "dark_crossings_estimated": int(latest_h["dark_crossings"]),
                "clandestine_rate_pct": round((latest_h["dark_crossings"] / (latest_h["active_vessels"] + latest_h["dark_crossings"])) * 100, 1),
            },
            "fujairah": {
                "tankers_anchored_today": int(latest_f["daily_tankers"]),
                "seven_day_ma": float(latest_f["seven_day_ma"]),
                "historical_5yr_avg": float(latest_f["historical_avg"]),
                "historical_min": float(latest_f["historical_min"]),
                "historical_max": float(latest_f["historical_max"]),
                "turnover_outflow_offset_pct": 50.0,
                "capacity_mbbls": round(latest_f["daily_tankers"] * 0.134, 1),
            },
            "bab_el_mandeb": {
                "traffic_today": int(latest_r["bem_daily"]),
                "seven_day_ma": float(latest_r["bem_7d_ma"]),
                "historical_5yr_avg": float(latest_r["bem_avg"]),
                "trend": "Restricted / Downward",
            },
            "suez_canal": {
                "traffic_today": int(latest_r["suez_daily"]),
                "seven_day_ma": float(latest_r["suez_7d_ma"]),
                "historical_5yr_avg": float(latest_r["suez_avg"]),
                "trend": "Elevated / Diverted Inflow",
            },
            "asian_demand_indices": {
                "china": float(latest_d["china_index"]),
                "china_reduction_pct": round(100.0 - float(latest_d["china_index"]), 1),
                "india": float(latest_d["india_index"]),
                "japan": float(latest_d["japan_index"]),
                "skorea": float(latest_d["skorea_index"]),
            }
        }


# Singleton instance
traffic_engine = TrafficAnalyticsEngine()
