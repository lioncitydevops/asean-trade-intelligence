# Skill: Macro Nowcast & Maritime Intelligence

## Objective
Your goal as the Quantitative Analyst (@quant) is to synthesize live AIS telemetry with macroeconomic models, dark fleet detection, and forward curve analysis.

## Instructions
1. **Telemetry Ingestion**: Step through AIS simulation or ingest live maritime feeds from `src/data/ais_stream.py`.
2. **Compute Geofence Metrics**: Calculate hourly/daily transit volume through key choke points:
   - Strait of Hormuz
   - Bab el-Mandeb
   - Strait of Malacca
   - Fujairah STS Anchorage
3. **Run Dark Fleet Detection**: Identify AIS transponder disabling anomalies, draft discrepancies, and ship-to-ship rendezvous within Fujairah coordinates.
4. **Compile Real-Time Report**: Run `python main.py --generate-pdf` or invoke `src.engine.pdf_generator.build_macro_newsletter_pdf` to generate the institutional PDF report.
5. **Macro Summary**: Output concise quantitative commentary synthesizing physical barrel movements against prompt Brent / horizon spreads.
