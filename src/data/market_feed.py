import random
import time
from typing import Dict, Any, List
from datetime import datetime, timezone


class LiveMarketFeed:
    """Simulates realistic real-time tick-by-tick crude oil futures pricing and forward curve structure."""

    def __init__(self):
        self.base_brent = 104.50
        self.current_brent = 104.50
        self.current_wti = 99.80
        self.current_dec = 101.20
        self.last_tick_time = time.time()
        self.total_data_points = 15_240_000_000

    def tick(self) -> Dict[str, Any]:
        """Apply real-time price fluctuation."""
        now = time.time()
        elapsed = now - self.last_tick_time
        self.last_tick_time = now

        # Random walk with slight mean reversion to $104.50
        drift = -0.05 * (self.current_brent - self.base_brent)
        shock = random.uniform(-0.12, 0.12)
        self.current_brent = round(max(95.0, min(115.0, self.current_brent + drift + shock)), 2)
        self.current_wti = round(self.current_brent - 4.70 + random.uniform(-0.05, 0.05), 2)
        self.current_dec = round(self.current_brent - 3.30 + random.uniform(-0.04, 0.04), 2)
        self.total_data_points += int(elapsed * 125000)

        spread = round(self.current_brent - (self.current_brent - 4.80), 2)
        m6_price = round(self.current_brent - 9.70, 2)
        prompt_m6_spread = f"+${round(self.current_brent - m6_price, 2):.2f}/bbl"

        return {
            "as_of_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "brent_prompt_price": self.current_brent,
            "wti_prompt_price": self.current_wti,
            "dec_horizon_price": self.current_dec,
            "forward_curve_structure": "Inverted / Steep Backwardation",
            "prompt_to_m6_spread": prompt_m6_spread,
            "total_data_points_day": f"{self.total_data_points / 1e9:.2f}B",
            "geopolitical_events": [
                {
                    "region": "Strait of Hormuz",
                    "status": "Restricted Navigation / Dark Fleet Dominance",
                    "impact": "Active transponder transits down >90%; clandestine night crossings via Fujairah STS.",
                },
                {
                    "region": "Bab El-Mandeb",
                    "status": "Houthi Blockade Restricting Saudi Tankers",
                    "impact": "Traffic down to 10-14 tankers/day (7-day MA); rerouting to Cape of Good Hope & Suez.",
                },
                {
                    "region": "Petroline (East-West Pipeline / Yanbu)",
                    "status": "Offline / Drone Strike Disruption",
                    "impact": "7M bpd pipeline capacity halted since Sep 12; Red Sea export relief valve closed.",
                },
                {
                    "region": "Asian Refining & Demand Hubs",
                    "status": "China Cushion vs India Opportunistic Buying",
                    "impact": "China seaborne imports down ~40% vs Feb baseline; India imports +38%.",
                },
            ],
            "forward_curve": [
                {"month": "Oct 2026 (Prompt)", "price": self.current_brent},
                {"month": "Nov 2026", "price": round(self.current_brent - 1.70, 2)},
                {"month": "Dec 2026", "price": self.current_dec},
                {"month": "Jan 2027", "price": round(self.current_brent - 5.90, 2)},
                {"month": "Feb 2027", "price": round(self.current_brent - 8.10, 2)},
                {"month": "Mar 2027", "price": round(self.current_brent - 9.70, 2)},
                {"month": "Jun 2027", "price": round(self.current_brent - 13.30, 2)},
                {"month": "Dec 2027", "price": round(self.current_brent - 17.00, 2)},
            ]
        }


_market_feed = LiveMarketFeed()


def get_market_intelligence(as_of_date: str = "2026-09-16") -> Dict[str, Any]:
    """Returns dynamic real-time market prices, forward curve inversion data, and supply disruption states."""
    data = _market_feed.tick()
    if as_of_date:
        data["as_of_date"] = as_of_date
    return data
