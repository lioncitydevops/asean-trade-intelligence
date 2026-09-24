"""
Google Cloud Dataflow (Apache Beam) Streaming Pipeline.
Ingests real-time AIS telemetry from Pub/Sub, executes spatial geofencing,
detects STS clusters and dark fleet crossings, and writes to BigQuery GIS.
"""

import json
import logging
from typing import Dict, Any, List

# Note: In GCP Dataflow runner, apache_beam is available.
# In local development, the pipeline can be tested with DirectRunner.
try:
    import apache_beam as beam
    from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
    from apache_beam.transforms.window import FixedWindows, SlidingWindows
except ImportError:
    beam = None


class ParseAISMessage(beam.DoFn if beam else object):
    """Parses raw JSON/NMEA AIS telemetry from Pub/Sub."""
    def process(self, element: bytes):
        try:
            record = json.loads(element.decode("utf-8"))
            # Standardize coordinates and types
            record["latitude"] = float(record["latitude"])
            record["longitude"] = float(record["longitude"])
            record["speed_knots"] = float(record.get("speed_knots", 0.0))
            record["draught_m"] = float(record.get("draught_m", 0.0))
            record["dwt_tonnes"] = float(record.get("dwt_tonnes", 100000.0))
            yield record
        except Exception as err:
            logging.error(f"Failed to parse AIS message: {err}")


class SpatialGeofencingFn(beam.DoFn if beam else object):
    """Evaluates spatial containment against Hormuz, Fujairah, Red Sea polygons."""
    def __init__(self, geofences_dict: Dict[str, Any]):
        self.geofences = geofences_dict

    def process(self, element: Dict[str, Any]):
        lat = element["latitude"]
        lon = element["longitude"]
        active = []

        # Simple point-in-box/polygon containment check
        if 25.7 <= lat <= 26.9 and 55.7 <= lon <= 56.9:
            active.append("HORMUZ")
        if 25.0 <= lat <= 25.45 and 56.35 <= lon <= 56.65:
            active.append("FUJAIRAH")
        if 12.3 <= lat <= 13.1 and 43.1 <= lon <= 43.6:
            active.append("BAB_EL_MANDEB")
        if 27.4 <= lat <= 30.1 and 32.3 <= lon <= 34.0:
            active.append("SUEZ")
        if 23.7 <= lat <= 24.2 and 37.8 <= lon <= 38.3:
            active.append("YANBU")

        element["active_geofences"] = active
        element["location"] = f"POINT({lon} {lat})"
        yield element


class DarkFleetDetectorFn(beam.DoFn if beam else object):
    """Identifies AIS blackout events in Hormuz and transit anomalies."""
    def process(self, element: Dict[str, Any]):
        is_dark = not element.get("is_transponder_on", True)
        if "HORMUZ" in element["active_geofences"] and is_dark:
            element["status"] = "Dark / AIS Disabled"
            logging.warning(f"DARK FLEET TRANSIT DETECTED: Vessel {element.get('vessel_name')} MMSI {element.get('mmsi')}")
        yield element


def run_pipeline(
    input_topic: str = "projects/maritime-oil-flow-prod/topics/ais-telemetry-raw",
    bq_output_table: str = "maritime-oil-flow-prod:maritime_intelligence.raw_ais_telemetry",
    pipeline_args: List[str] = None
):
    """Builds and executes the streaming Beam pipeline."""
    if not beam:
        raise RuntimeError("Apache Beam is required to run this pipeline.")

    options = PipelineOptions(pipeline_args, streaming=True)
    with beam.Pipeline(options=options) as p:
        raw_stream = (
            p
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(topic=input_topic)
            | "ParseAIS" >> beam.ParDo(ParseAISMessage())
            | "SpatialGeofence" >> beam.ParDo(SpatialGeofencingFn({}))
            | "DarkFleetFilter" >> beam.ParDo(DarkFleetDetectorFn())
        )

        # Write to BigQuery streaming buffer
        _ = (
            raw_stream
            | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
                table=bq_output_table,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
            )
        )
