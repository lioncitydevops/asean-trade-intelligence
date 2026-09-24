"""
High-resolution financial and maritime chart renderer for institutional macro research aesthetics.
"""

import os
from typing import Dict, List, Tuple
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime
from ..data.historical_baselines import generate_time_series_data


# Chart theme styling constants
THEME = {
    "bg_color": "#12171E",
    "plot_bg": "#12171E",
    "grid_color": "#222B38",
    "text_color": "#E1E6ED",
    "muted_text": "#8C9BAE",
    "yellow_line": "#E5B834",
    "avg_line": "#488AC7",
    "band_fill": "#1E334D",
    "china_color": "#29B6F6",
    "india_color": "#FFCA28",
    "japan_color": "#FFA726",
    "skorea_color": "#EC407A",
}


def setup_dark_style(ax):
    """Applies institutional dark theme formatting to Matplotlib axes."""
    ax.set_facecolor(THEME["plot_bg"])
    ax.grid(True, linestyle="--", linewidth=0.6, color=THEME["grid_color"], alpha=0.8)
    ax.tick_params(colors=THEME["muted_text"], labelsize=8, direction="out", length=3)
    for spine in ax.spines.values():
        spine.set_color(THEME["grid_color"])
        spine.set_linewidth(0.8)


def render_exhibit_1(df: pd.DataFrame, output_path: str = "output/exhibit_1.png"):
    """
    Renders Exhibit 1: Fujairah: Daily Number of Tankers Anchored (7-day moving average).
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 3.4), dpi=300, facecolor=THEME["bg_color"])
    setup_dark_style(ax)

    dates = df["date"]
    
    # Fill 5-yr Min-Max envelope
    ax.fill_between(
        dates, df["historical_min"], df["historical_max"],
        color=THEME["band_fill"], alpha=0.7, label="Min-Max (2020-2025)"
    )
    
    # 5-yr Average dotted line
    ax.plot(
        dates, df["historical_avg"],
        color=THEME["avg_line"], linestyle=":", linewidth=1.2, label="Average (2021-2025)"
    )
    
    # 2026 Actual 7-day MA line
    ax.plot(
        dates, df["seven_day_ma"],
        color=THEME["yellow_line"], linewidth=1.8, label="2026"
    )

    ax.set_ylabel("Number of ships", color=THEME["text_color"], fontsize=8, labelpad=6)
    ax.set_ylim(0, 80)
    ax.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80])

    # Date formatting (full year Jan-Dec)
    ax.set_xlim(datetime(2026, 1, 1), datetime(2026, 12, 31))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    # Legend at bottom
    leg = ax.legend(
        loc="lower center", bbox_to_anchor=(0.5, -0.22),
        ncol=3, frameon=False, fontsize=7.5
    )
    for text in leg.get_texts():
        text.set_color(THEME["text_color"])

    plt.tight_layout()
    fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    return output_path


def render_exhibit_2(df: pd.DataFrame, output_path: str = "output/exhibit_2.png"):
    """
    Renders Exhibit 2: Bab El-Mandeb and Suez Canal: Daily Tanker Traffic (7-day moving average).
    Dual-panel plot.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.2), dpi=300, facecolor=THEME["bg_color"])
    
    dates = df["date"]

    # Panel 1: Bab El-Mandeb Strait
    setup_dark_style(ax1)
    ax1.set_title("Bab El-Mandeb Strait", color=THEME["text_color"], fontsize=8, pad=4)
    ax1.fill_between(dates, df["bem_min"], df["bem_max"], color=THEME["band_fill"], alpha=0.7, label="Min-Max (2020-2025)")
    ax1.plot(dates, df["bem_avg"], color=THEME["avg_line"], linestyle=":", linewidth=1.1, label="Average (2020-2025)")
    ax1.plot(dates, df["bem_7d_ma"], color=THEME["yellow_line"], linewidth=1.6, label="2026")
    ax1.set_ylabel("Number of vessels", color=THEME["text_color"], fontsize=7.5)
    ax1.set_ylim(0, 40)
    ax1.set_yticks([0, 5, 10, 15, 20, 25, 30, 35, 40])
    ax1.set_xlim(datetime(2026, 1, 1), datetime(2026, 12, 31))
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    # Panel 2: Suez Canal
    setup_dark_style(ax2)
    ax2.set_title("Suez Canal", color=THEME["text_color"], fontsize=8, pad=4)
    ax2.fill_between(dates, df["suez_min"], df["suez_max"], color=THEME["band_fill"], alpha=0.7)
    ax2.plot(dates, df["suez_avg"], color=THEME["avg_line"], linestyle=":", linewidth=1.1)
    ax2.plot(dates, df["suez_7d_ma"], color=THEME["yellow_line"], linewidth=1.6)
    ax2.set_ylim(0, 40)
    ax2.set_yticks([0, 5, 10, 15, 20, 25, 30, 35, 40])
    ax2.set_xlim(datetime(2026, 1, 1), datetime(2026, 12, 31))
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    # Shared bottom legend
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(
        handles, labels, loc="lower center", bbox_to_anchor=(0.5, -0.06),
        ncol=3, frameon=False, fontsize=7.5
    )
    for text in fig.legends[0].get_texts():
        text.set_color(THEME["text_color"])

    plt.tight_layout()
    fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    return output_path


def render_exhibit_3(df: pd.DataFrame, output_path: str = "output/exhibit_3.png"):
    """
    Renders Exhibit 3: China, India, Japan & South Korea: Seaborne Oil Imports (30-day moving average).
    Rebased: 100 = 2026-02-28.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 3.4), dpi=300, facecolor=THEME["bg_color"])
    setup_dark_style(ax)

    dates = df["date"]
    ax.plot(dates, df["japan_index"], color=THEME["japan_color"], linewidth=1.4, label="Japan")
    ax.plot(dates, df["china_index"], color=THEME["china_color"], linewidth=1.6, label="China")
    ax.plot(dates, df["skorea_index"], color=THEME["skorea_color"], linewidth=1.4, label="South Korea")
    ax.plot(dates, df["india_index"], color=THEME["india_color"], linewidth=1.6, label="India")

    ax.set_ylabel("Rebased: 100 = 2026-02-28", color=THEME["text_color"], fontsize=8, labelpad=6)
    ax.set_ylim(50, 150)
    ax.set_yticks([60, 80, 100, 120, 140])

    # Date formatting
    ax.set_xlim(datetime(2026, 1, 1), datetime(2026, 9, 20))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    # Bottom legend
    leg = ax.legend(
        loc="lower center", bbox_to_anchor=(0.5, -0.22),
        ncol=4, frameon=False, fontsize=7.5
    )
    for text in leg.get_texts():
        text.set_color(THEME["text_color"])

    plt.tight_layout()
    fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    return output_path


def render_all_exhibits(output_dir: str = "output") -> Dict[str, str]:
    """Generates high-resolution PNG charts for all 3 exhibits."""
    data = generate_time_series_data()
    ex1_path = render_exhibit_1(data["fujairah"], os.path.join(output_dir, "exhibit_1.png"))
    ex2_path = render_exhibit_2(data["redsea"], os.path.join(output_dir, "exhibit_2.png"))
    ex3_path = render_exhibit_3(data["asian_demand"], os.path.join(output_dir, "exhibit_3.png"))
    return {
        "exhibit_1": ex1_path,
        "exhibit_2": ex2_path,
        "exhibit_3": ex3_path,
    }
