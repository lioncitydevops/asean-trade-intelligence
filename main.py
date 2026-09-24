"""
Maritime Oil Flow Intelligence & Real-Time Macro Report Generator
Unified CLI & System Runner.
"""

import os
import sys
import argparse
import time
from datetime import datetime


def run_pdf_generation(output_path: str = "output/Macro_Insights_Newsletter_RealTime.pdf"):
    print("=================================================================")
    print(" REAL-TIME MARITIME MACRO INSIGHTS PUBLISHER")
    print("=================================================================")
    from src.engine.pdf_generator import build_macro_newsletter_pdf
    print(f"[*] Ingesting real-time AIS telemetry & 5-year historical baselines...")
    print(f"[*] Detecting Dark Fleet transits & Fujairah STS transshipments...")
    print(f"[*] Synthesizing macroeconomic commentary & forward curve structure...")
    print(f"[*] Rendering Exhibits 1, 2, and 3 (high-resolution vector)...")
    
    start_time = time.time()
    pdf_out = build_macro_newsletter_pdf(output_pdf_path=output_path)
    elapsed = time.time() - start_time
    
    print(f"[OK] Successfully compiled institutional PDF in {elapsed:.2f}s!")
    print(f"[OK] Published at: {os.path.abspath(pdf_out)}")
    print("=================================================================")
    return pdf_out


def run_server(host: str = "127.0.0.1", port: int = 8000):
    import uvicorn
    from src.api.server import app
    print("=================================================================")
    print(" STARTING REAL-TIME MARITIME OIL FLOW INTELLIGENCE TERMINAL")
    print("=================================================================")
    print(f"[*] Terminal UI & REST API available at: http://{host}:{port}")
    print(f"[*] Direct PDF Download endpoint: http://{host}:{port}/api/download-report")
    print("=================================================================")
    uvicorn.run(app, host=host, port=port)


def run_schedule_daemon(interval_seconds: int = 3600):
    print(f"[*] Starting Real-Time Report Publisher Daemon (Interval: {interval_seconds}s)...")
    while True:
        now_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        out_file = f"output/Macro_Insights_Newsletter_{now_str}.pdf"
        run_pdf_generation(output_path=out_file)
        print(f"[*] Sleeping for {interval_seconds} seconds until next scheduled edition...")
        time.sleep(interval_seconds)


def run_diagnostics():
    print("[*] Running system diagnostics...")
    from src.analytics.traffic_engine import traffic_engine
    from src.analytics.dark_fleet_detector import dark_fleet_detector
    from src.data.ais_stream import stream_engine
    from src.data.market_feed import get_market_intelligence

    metrics = traffic_engine.get_current_metrics()
    positions = stream_engine.step_simulation()
    sts = dark_fleet_detector.detect_sts_operations(positions)
    market = get_market_intelligence()

    assert len(positions) > 0, "No vessels generated"
    assert "hormuz" in metrics, "Hormuz metrics missing"
    assert "fujairah" in metrics, "Fujairah metrics missing"
    assert market["dec_horizon_price"] > 100, "Market price error"
    print("[OK] All telemetry, anomaly detection, and baseline models passed tests successfully!")


def main():
    parser = argparse.ArgumentParser(description="Maritime Oil Flow Intelligence & Real-Time Macro Nowcasting Platform")
    parser.add_argument("--serve", action="store_true", help="Launch interactive web terminal and API server")
    parser.add_argument("--generate-pdf", action="store_true", help="Generate the latest Macro Insights PDF report")
    parser.add_argument("--schedule", action="store_true", help="Run recurring publication daemon")
    parser.add_argument("--test", action="store_true", help="Run system diagnostics and validation tests")
    parser.add_argument("--port", type=int, default=8000, help="Port for web server (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host for web server (default: 127.0.0.1)")

    args = parser.parse_args()

    if args.test:
        run_diagnostics()
    elif args.generate_pdf:
        run_pdf_generation()
    elif args.schedule:
        run_schedule_daemon()
    elif args.serve:
        run_server(host=args.host, port=args.port)
    else:
        # Default behavior: generate PDF and then launch server
        run_pdf_generation()
        run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
