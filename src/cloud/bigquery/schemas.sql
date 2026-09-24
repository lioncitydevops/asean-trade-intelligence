-- ==============================================================================
-- Google Cloud BigQuery GIS Data Schemas & Analytic Views
-- Real-Time Maritime Oil Flow Intelligence & 5-Year Macro Baselines
-- ==============================================================================

-- 1. Raw AIS Telemetry Partitioned Table
CREATE TABLE IF NOT EXISTS `quantcube_maritime.raw_ais_telemetry`
(
  mmsi INT64 NOT NULL,
  imo INT64,
  vessel_name STRING NOT NULL,
  vessel_type STRING NOT NULL, -- 'VLCC', 'Suezmax', 'Aframax', 'Shuttle Tanker', 'Bunker Tanker'
  location GEOGRAPHY NOT NULL,  -- ST_GEOGPOINT(longitude, latitude)
  speed_knots FLOAT64,
  heading_deg FLOAT64,
  draught_m FLOAT64,
  max_draught_m FLOAT64,
  dwt_tonnes FLOAT64,
  destination STRING,
  is_transponder_on BOOL DEFAULT TRUE,
  status STRING,                -- 'Underway', 'Anchored', 'STS Transfer', 'Dark Transit'
  active_geofences ARRAY<STRING>,
  timestamp TIMESTAMP NOT NULL
)
PARTITION BY DATE(timestamp)
CLUSTER BY vessel_type, status, mmsi
OPTIONS (
  description = "High-frequency partitioned AIS maritime telemetry stream",
  require_partition_filter = FALSE
);

-- 2. Chokepoint Transit Events Table
CREATE TABLE IF NOT EXISTS `quantcube_maritime.chokepoint_transits`
(
  transit_id STRING NOT NULL,
  chokepoint STRING NOT NULL,   -- 'HORMUZ', 'FUJAIRAH', 'BAB_EL_MANDEB', 'SUEZ', 'YANBU'
  mmsi INT64 NOT NULL,
  vessel_name STRING,
  vessel_type STRING,
  direction STRING,             -- 'Outbound', 'Inbound', 'Northbound', 'Southbound'
  transit_timestamp TIMESTAMP NOT NULL,
  estimated_cargo_bbls FLOAT64,
  is_dark BOOL DEFAULT FALSE,
  details STRING
)
PARTITION BY DATE(transit_timestamp)
CLUSTER BY chokepoint, vessel_type;

-- 3. Ship-to-Ship (STS) Lightering Detection Log
CREATE TABLE IF NOT EXISTS `quantcube_maritime.sts_lightering_events`
(
  cluster_id STRING NOT NULL,
  mother_mmsi INT64,
  mother_name STRING,
  mother_type STRING,
  daughter_mmsi INT64,
  daughter_name STRING,
  daughter_type STRING,
  location GEOGRAPHY NOT NULL,
  start_time TIMESTAMP NOT NULL,
  duration_hours FLOAT64,
  distance_meters FLOAT64,
  estimated_transferred_bbls FLOAT64,
  anchorage_zone STRING
)
PARTITION BY DATE(start_time)
CLUSTER BY anchorage_zone, mother_type;

-- 4. Historical 5-Year Baselines Lookup Table (2020-2025)
CREATE TABLE IF NOT EXISTS `quantcube_maritime.historical_5yr_baselines`
(
  day_of_year INT64 NOT NULL,   -- 1 to 366
  chokepoint STRING NOT NULL,   -- 'FUJAIRAH', 'BAB_EL_MANDEB', 'SUEZ'
  min_vessels FLOAT64 NOT NULL,
  max_vessels FLOAT64 NOT NULL,
  avg_vessels FLOAT64 NOT NULL,
  avg_capacity_mbbls FLOAT64
)
CLUSTER BY chokepoint;

-- ==============================================================================
-- ANALYTICAL QUERIES FOR REPORT EXHIBITS
-- ==============================================================================

-- Query for Exhibit 1: Fujairah Anchorage Daily Tankers vs 5-Yr Baseline
-- Computes rolling 7-day moving average and joins historical Min/Max/Avg envelope
CREATE OR REPLACE VIEW `quantcube_maritime.view_exhibit1_fujairah` AS
WITH daily_anchorage AS (
  SELECT
    DATE(timestamp) AS transit_date,
    EXTRACT(DAYOFYEAR FROM DATE(timestamp)) AS day_of_year,
    COUNT(DISTINCT mmsi) AS daily_tankers
  FROM `quantcube_maritime.raw_ais_telemetry`
  WHERE 'FUJAIRAH' IN UNNEST(active_geofences)
    AND (speed_knots < 2.0 OR status IN ('Anchored', 'STS Transfer'))
  GROUP BY 1, 2
),
rolling_ma AS (
  SELECT
    transit_date,
    day_of_year,
    daily_tankers,
    AVG(daily_tankers) OVER (
      ORDER BY transit_date
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS seven_day_ma
  FROM daily_anchorage
)
SELECT
  r.transit_date,
  r.daily_tankers,
  ROUND(r.seven_day_ma, 1) AS seven_day_ma,
  b.min_vessels AS historical_min,
  b.max_vessels AS historical_max,
  b.avg_vessels AS historical_avg
FROM rolling_ma r
LEFT JOIN `quantcube_maritime.historical_5yr_baselines` b
  ON r.day_of_year = b.day_of_year AND b.chokepoint = 'FUJAIRAH'
ORDER BY r.transit_date;

-- Query for Exhibit 2: Bab El-Mandeb vs Suez Canal Divergence
CREATE OR REPLACE VIEW `quantcube_maritime.view_exhibit2_redsea` AS
WITH daily_transits AS (
  SELECT
    DATE(transit_timestamp) AS transit_date,
    COUNT(DISTINCT IF(chokepoint = 'BAB_EL_MANDEB', mmsi, NULL)) AS bem_daily,
    COUNT(DISTINCT IF(chokepoint = 'SUEZ', mmsi, NULL)) AS suez_daily
  FROM `quantcube_maritime.chokepoint_transits`
  GROUP BY 1
)
SELECT
  transit_date,
  bem_daily,
  ROUND(AVG(bem_daily) OVER (ORDER BY transit_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS bem_7d_ma,
  suez_daily,
  ROUND(AVG(suez_daily) OVER (ORDER BY transit_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS suez_7d_ma
FROM daily_transits
ORDER BY transit_date;

-- Query for Exhibit 3: Asian Seaborne Imports Nowcast (30-day MA, Rebased 100)
CREATE OR REPLACE VIEW `quantcube_maritime.view_exhibit3_asian_demand` AS
WITH discharge_flows AS (
  SELECT
    DATE(timestamp) AS event_date,
    SUM(IF('CHINA_PORTS' IN UNNEST(active_geofences), (dwt_tonnes * 7.33 * 0.85) / 1000000, 0)) AS china_mbbls,
    SUM(IF('INDIA_PORTS' IN UNNEST(active_geofences), (dwt_tonnes * 7.33 * 0.85) / 1000000, 0)) AS india_mbbls,
    SUM(IF('JAPAN_PORTS' IN UNNEST(active_geofences), (dwt_tonnes * 7.33 * 0.85) / 1000000, 0)) AS japan_mbbls,
    SUM(IF('SKOREA_PORTS' IN UNNEST(active_geofences), (dwt_tonnes * 7.33 * 0.85) / 1000000, 0)) AS skorea_mbbls
  FROM `quantcube_maritime.raw_ais_telemetry`
  GROUP BY 1
),
smoothed_30d AS (
  SELECT
    event_date,
    AVG(china_mbbls) OVER (ORDER BY event_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS china_30d,
    AVG(india_mbbls) OVER (ORDER BY event_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS india_30d,
    AVG(japan_mbbls) OVER (ORDER BY event_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS japan_30d,
    AVG(skorea_mbbls) OVER (ORDER BY event_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS skorea_30d
  FROM discharge_flows
),
baseline_val AS (
  SELECT
    china_30d AS c_base,
    india_30d AS i_base,
    japan_30d AS j_base,
    skorea_30d AS k_base
  FROM smoothed_30d
  WHERE event_date = '2026-02-28'
  LIMIT 1
)
SELECT
  s.event_date,
  ROUND((s.china_30d / b.c_base) * 100.0, 1) AS china_index,
  ROUND((s.india_30d / b.i_base) * 100.0, 1) AS india_index,
  ROUND((s.japan_30d / b.j_base) * 100.0, 1) AS japan_index,
  ROUND((s.skorea_30d / b.k_base) * 100.0, 1) AS skorea_index
FROM smoothed_30d s
CROSS JOIN baseline_val b
ORDER BY s.event_date;
