"""
High-resolution financial and maritime chart renderer for institutional macro research aesthetics.
Rendered in clean, professional plain colours (neutral monochrome / grayscale palette).
"""

import os
from typing import Dict, List, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False
    plt = None
    mdates = None

from ..data.historical_baselines import generate_time_series_data


# Plain colours chart theme styling
THEME = {
    "bg_color": "#FFFFFF",
    "plot_bg": "#FFFFFF",
    "grid_color": "#E5E7EB",
    "text_color": "#111827",
    "muted_text": "#4B5563",
    "actual_line": "#111827",      # Solid Black
    "avg_line": "#4B5563",         # Dark Slate Dotted
    "band_fill": "#F3F4F6",        # Light Neutral Gray Fill
    "line_china": "#111827",       # Solid Black
    "line_india": "#374151",       # Charcoal Slate (Dashed)
    "line_japan": "#64748B",       # Slate Gray (Dotted)
    "line_skorea": "#9CA3AF",      # Neutral Gray (Dash-dot)
}


def setup_plain_style(ax):
    """Applies institutional plain colours formatting to Matplotlib axes."""
    ax.set_facecolor(THEME["plot_bg"])
    ax.grid(True, linestyle="--", linewidth=0.6, color=THEME["grid_color"], alpha=0.9)
    ax.tick_params(colors=THEME["muted_text"], labelsize=8, direction="out", length=3)
    for spine in ax.spines.values():
        spine.set_color("#CBD5E1")
        spine.set_linewidth(0.8)


def render_exhibit_1(df: pd.DataFrame, output_path: str = "output/exhibit_1.png"):
    """
    Renders Exhibit 1: Fujairah: Daily Number of Tankers Anchored (7-day moving average).
    Rendered in plain colours.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 3.4), dpi=300, facecolor=THEME["bg_color"])
    setup_plain_style(ax)

    dates = pd.to_datetime(df["date"])
    
    # Fill 5-yr Min-Max envelope in light neutral gray
    ax.fill_between(
        dates, df["historical_min"], df["historical_max"],
        color=THEME["band_fill"], alpha=0.9, label="Min-Max (2020-2025)"
    )
    
    # 5-yr Average dotted line
    ax.plot(
        dates, df["historical_avg"],
        color=THEME["avg_line"], linestyle=":", linewidth=1.3, label="Average (2021-2025)"
    )
    
    # Actual 7-day MA line in solid black
    ax.plot(
        dates, df["seven_day_ma"],
        color=THEME["actual_line"], linewidth=2.0, label="Current Year (7d MA)"
    )

    ax.set_ylabel("Number of ships", color=THEME["text_color"], fontsize=8, labelpad=6)
    ax.set_ylim(0, 80)
    ax.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80])

    # Date formatting
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
    Rendered in plain colours.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.2), dpi=300, facecolor=THEME["bg_color"])
    
    dates = pd.to_datetime(df["date"])

    # Panel 1: Bab El-Mandeb Strait
    setup_plain_style(ax1)
    ax1.set_title("Bab El-Mandeb Strait", color=THEME["text_color"], fontsize=8.5, fontweight="bold", pad=4)
    ax1.fill_between(dates, df["bem_min"], df["bem_max"], color=THEME["band_fill"], alpha=0.9, label="Min-Max (2020-2025)")
    ax1.plot(dates, df["bem_avg"], color=THEME["avg_line"], linestyle=":", linewidth=1.2, label="Average (2020-2025)")
    ax1.plot(dates, df["bem_7d_ma"], color=THEME["actual_line"], linewidth=1.8, label="Current Year (7d MA)")
    ax1.set_ylabel("Number of vessels", color=THEME["text_color"], fontsize=7.5)
    ax1.set_ylim(0, 40)
    ax1.set_yticks([0, 5, 10, 15, 20, 25, 30, 35, 40])
    ax1.set_xlim(datetime(2026, 1, 1), datetime(2026, 12, 31))
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    # Panel 2: Suez Canal
    setup_plain_style(ax2)
    ax2.set_title("Suez Canal", color=THEME["text_color"], fontsize=8.5, fontweight="bold", pad=4)
    ax2.fill_between(dates, df["suez_min"], df["suez_max"], color=THEME["band_fill"], alpha=0.9)
    ax2.plot(dates, df["suez_avg"], color=THEME["avg_line"], linestyle=":", linewidth=1.2)
    ax2.plot(dates, df["suez_7d_ma"], color=THEME["actual_line"], linewidth=1.8)
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
    Rendered in plain colours with distinctive monochrome line styles.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 3.4), dpi=300, facecolor=THEME["bg_color"])
    setup_plain_style(ax)

    dates = pd.to_datetime(df["date"])
    ax.plot(dates, df["china_index"], color=THEME["line_china"], linestyle="-", linewidth=2.0, label="China")
    ax.plot(dates, df["india_index"], color=THEME["line_india"], linestyle="--", linewidth=1.7, label="India")
    ax.plot(dates, df["japan_index"], color=THEME["line_japan"], linestyle=":", linewidth=1.5, label="Japan")
    ax.plot(dates, df["skorea_index"], color=THEME["line_skorea"], linestyle="-.", linewidth=1.5, label="South Korea")

    ax.set_ylabel("Rebased Index (100 = Baseline)", color=THEME["text_color"], fontsize=8, labelpad=6)
    ax.set_ylim(50, 150)
    ax.set_yticks([60, 80, 100, 120, 140])

    # Date formatting dynamically up to current dataset max date
    max_d = max(dates.max(), datetime(2026, 10, 21))
    ax.set_xlim(datetime(2026, 1, 1), max_d)
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


def render_all_exhibits(output_dir: str = "output", as_of_date: str = None) -> Dict[str, str]:
    """Generates high-resolution PNG charts for all exhibits in plain colours."""
    data = generate_time_series_data(as_of_date=as_of_date)
    ex1_path = render_exhibit_1(data["fujairah"], os.path.join(output_dir, "exhibit_1.png"))
    ex2_path = render_exhibit_2(data["redsea"], os.path.join(output_dir, "exhibit_2.png"))
    ex3_path = render_exhibit_3(data["asian_demand"], os.path.join(output_dir, "exhibit_3.png"))
    return {
        "exhibit_1": ex1_path,
        "exhibit_2": ex2_path,
        "exhibit_3": ex3_path,
    }
