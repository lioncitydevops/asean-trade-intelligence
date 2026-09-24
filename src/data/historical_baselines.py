"""
Historical baseline generation and ground-truth metrics calibration matching the 5-year institutional dataset.
"""

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


def generate_time_series_data(as_of_date: str = "2026-09-15") -> Dict[str, pd.DataFrame]:
    """
    Generates realistic daily historical data from 2026-01-01 through as_of_date,
    along with 5-year historical baselines (2020-2025 Min, Max, Avg) and Asian demand indices.
    """
    end_dt = datetime.strptime(as_of_date, "%Y-%m-%d")
    start_dt = datetime(2026, 1, 1)
    date_range = pd.date_range(start=start_dt, end=end_dt, freq="D")
    n_days = len(date_range)
    day_indices = np.arange(n_days)

    # 1. Fujairah Anchorage Tankers Anchored (Exhibit 1)
    # 5-year baseline: Min ~30-35, Max ~65-75, Avg ~48-52
    np.random.seed(42)
    fujairah_min = 32 + 5 * np.sin(np.linspace(0, 3.14, 365))[:n_days] + np.random.normal(0, 1.5, n_days)
    fujairah_max = 68 + 7 * np.sin(np.linspace(0, 3.14, 365))[:n_days] + np.random.normal(0, 2.0, n_days)
    fujairah_avg = 48 + 3 * np.sin(np.linspace(0, 3.14, 365))[:n_days] + np.random.normal(0, 0.8, n_days)

    # 2026 trajectory:
    # Jan-Feb: 40-48 (44 on Feb 28)
    # March: Sudden collapse to ~0-5 (strike in zone)
    # April-June: Gradual bottoming out (5-18)
    # Late June: US-Iran MoU spike to 50
    # July-Sep: Holds strong at 52-67 (67 on Sep 14)
    fujairah_actual_daily = np.zeros(n_days)
    feb_28_idx = (datetime(2026, 2, 28) - start_dt).days
    march_15_idx = (datetime(2026, 3, 15) - start_dt).days
    june_20_idx = (datetime(2026, 6, 20) - start_dt).days
    july_15_idx = (datetime(2026, 7, 15) - start_dt).days

    for i in range(n_days):
        if i <= feb_28_idx:
            fujairah_actual_daily[i] = 42 + 4 * np.sin(i / 10) + np.random.normal(0, 2)
            if i == feb_28_idx:
                fujairah_actual_daily[i] = 44.0
        elif i < march_15_idx:
            # Drop off cliff
            progress = (i - feb_28_idx) / (march_15_idx - feb_28_idx)
            fujairah_actual_daily[i] = max(1.0, 44.0 * (1.0 - progress) + np.random.normal(0, 1))
        elif i < june_20_idx:
            # Sluggish period (3 - 18)
            t = (i - march_15_idx) / (june_20_idx - march_15_idx)
            fujairah_actual_daily[i] = 4.0 + 12.0 * t + 3 * np.sin(i / 5) + np.random.normal(0, 1.5)
        elif i < july_15_idx:
            # Rapid recovery following late June MoU
            t = (i - june_20_idx) / (july_15_idx - june_20_idx)
            fujairah_actual_daily[i] = 16.0 + 36.0 * t + np.random.normal(0, 2)
        else:
            # Elevated transshipment hub load: 52 to 67
            t = (i - july_15_idx) / max(1, n_days - july_15_idx)
            fujairah_actual_daily[i] = 52.0 + 15.0 * t + 2.5 * np.sin(i / 7) + np.random.normal(0, 2)

    fujairah_7d_ma = pd.Series(fujairah_actual_daily).rolling(7, min_periods=1).mean().values

    fujairah_df = pd.DataFrame({
        "date": date_range,
        "date_str": [d.strftime("%Y-%m-%d") for d in date_range],
        "daily_tankers": np.round(fujairah_actual_daily).astype(int),
        "seven_day_ma": np.round(fujairah_7d_ma, 1),
        "historical_min": np.round(fujairah_min, 1),
        "historical_max": np.round(fujairah_max, 1),
        "historical_avg": np.round(fujairah_avg, 1),
    })

    # 2. Bab El-Mandeb and Suez Canal (Exhibit 2)
    # Bab El-Mandeb: Min 10-15, Max 28-35, Avg ~20-22
    # 2026: Jan-Feb ~18-22, March-July ~16-20, Aug-Sep declines to 10-14
    bem_min = 10 + 2 * np.sin(np.linspace(0, 3.14, 365))[:n_days]
    bem_max = 30 + 3 * np.sin(np.linspace(0, 3.14, 365))[:n_days]
    bem_avg = 20 + 1.5 * np.sin(np.linspace(0, 3.14, 365))[:n_days]

    bem_daily = np.zeros(n_days)
    aug_1_idx = (datetime(2026, 8, 1) - start_dt).days
    for i in range(n_days):
        if i < aug_1_idx:
            bem_daily[i] = 19.0 + 2.5 * np.sin(i / 8) + np.random.normal(0, 2)
        else:
            # Houthi restrictions tighten
            t = (i - aug_1_idx) / max(1, n_days - aug_1_idx)
            bem_daily[i] = 18.0 - 7.0 * t + 1.5 * np.sin(i / 6) + np.random.normal(0, 1.5)
    bem_7d_ma = pd.Series(bem_daily).rolling(7, min_periods=1).mean().values

    # Suez Canal: Min 8-12, Max 28-32, Avg ~16-18
    # 2026: Jan-June ~15-17, July-Sep rises to 21-24 (traffic redirected)
    suez_min = 9 + 2 * np.sin(np.linspace(0, 3.14, 365))[:n_days]
    suez_max = 30 + 2 * np.sin(np.linspace(0, 3.14, 365))[:n_days]
    suez_avg = 16.5 + 1.0 * np.sin(np.linspace(0, 3.14, 365))[:n_days]

    suez_daily = np.zeros(n_days)
    for i in range(n_days):
        if i < aug_1_idx:
            suez_daily[i] = 15.5 + 1.8 * np.sin(i / 10) + np.random.normal(0, 1.8)
        else:
            t = (i - aug_1_idx) / max(1, n_days - aug_1_idx)
            suez_daily[i] = 16.0 + 6.5 * t + 1.5 * np.sin(i / 6) + np.random.normal(0, 1.5)
    suez_7d_ma = pd.Series(suez_daily).rolling(7, min_periods=1).mean().values

    redsea_df = pd.DataFrame({
        "date": date_range,
        "date_str": [d.strftime("%Y-%m-%d") for d in date_range],
        "bem_daily": np.round(bem_daily).astype(int),
        "bem_7d_ma": np.round(bem_7d_ma, 1),
        "bem_min": np.round(bem_min, 1),
        "bem_max": np.round(bem_max, 1),
        "bem_avg": np.round(bem_avg, 1),
        "suez_daily": np.round(suez_daily).astype(int),
        "suez_7d_ma": np.round(suez_7d_ma, 1),
        "suez_min": np.round(suez_min, 1),
        "suez_max": np.round(suez_max, 1),
        "suez_avg": np.round(suez_avg, 1),
    })

    # 3. Asian Seaborne Oil Imports (Exhibit 3 - 30-day moving average, Rebased 100 = 2026-02-28)
    # China: drops by ~40% (down to ~60 index) by May/June, stays at 60-65
    # India: surges up to 135-145 in summer
    # Japan: 90-115
    # South Korea: 85-110
    china_raw = np.ones(n_days) * 100.0
    india_raw = np.ones(n_days) * 100.0
    japan_raw = np.ones(n_days) * 100.0
    skorea_raw = np.ones(n_days) * 100.0

    may_1_idx = (datetime(2026, 5, 1) - start_dt).days

    for i in range(n_days):
        # China
        if i <= feb_28_idx:
            china_raw[i] = 100.0 + np.random.normal(0, 3)
        elif i < may_1_idx:
            t = (i - feb_28_idx) / (may_1_idx - feb_28_idx)
            china_raw[i] = 100.0 - 40.0 * t + np.random.normal(0, 3)
        else:
            china_raw[i] = 60.0 + 4.0 * np.sin(i / 15) + np.random.normal(0, 2.5)

        # India
        if i <= feb_28_idx:
            india_raw[i] = 100.0 + np.random.normal(0, 4)
        elif i < june_20_idx:
            t = (i - feb_28_idx) / (june_20_idx - feb_28_idx)
            india_raw[i] = 100.0 + 38.0 * t + np.random.normal(0, 4)
        else:
            india_raw[i] = 138.0 + 6.0 * np.sin(i / 12) + np.random.normal(0, 3.5)

        # Japan
        japan_raw[i] = 102.0 + 7.0 * np.sin(i / 20) + np.random.normal(0, 3)

        # South Korea
        skorea_raw[i] = 98.0 + 8.0 * np.cos(i / 18) + np.random.normal(0, 3)

    # 30-day moving average
    china_30d = pd.Series(china_raw).rolling(30, min_periods=1).mean().values
    india_30d = pd.Series(india_raw).rolling(30, min_periods=1).mean().values
    japan_30d = pd.Series(japan_raw).rolling(30, min_periods=1).mean().values
    skorea_30d = pd.Series(skorea_raw).rolling(30, min_periods=1).mean().values

    # Normalize to 100.0 on Feb 28
    c_base = china_30d[feb_28_idx]
    i_base = india_30d[feb_28_idx]
    j_base = japan_30d[feb_28_idx]
    k_base = skorea_30d[feb_28_idx]

    asian_demand_df = pd.DataFrame({
        "date": date_range,
        "date_str": [d.strftime("%Y-%m-%d") for d in date_range],
        "china_index": np.round(china_30d / c_base * 100.0, 1),
        "india_index": np.round(india_30d / i_base * 100.0, 1),
        "japan_index": np.round(japan_30d / j_base * 100.0, 1),
        "skorea_index": np.round(skorea_30d / k_base * 100.0, 1),
    })

    # 4. Hormuz Chokepoint & Yanbu Petroline Metrics
    hormuz_df = pd.DataFrame({
        "date": date_range,
        "date_str": [d.strftime("%Y-%m-%d") for d in date_range],
        "active_vessels": [46 if i <= feb_28_idx else max(2, int(46 - (i - feb_28_idx) * 0.22 + np.random.normal(0, 1.5))) for i in range(n_days)],
        "dark_crossings": [2 if i <= feb_28_idx else int(8 + (i - feb_28_idx) * 0.12 + np.random.normal(0, 2)) for i in range(n_days)],
    })

    return {
        "fujairah": fujairah_df,
        "redsea": redsea_df,
        "asian_demand": asian_demand_df,
        "hormuz": hormuz_df,
    }
