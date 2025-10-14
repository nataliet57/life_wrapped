from pathlib import Path
import calendar

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.colors import LinearSegmentedColormap

from life_wrapped.models import month_map

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"


def generate_calendar_heatmap(month_bucket, output_dir=OUTPUTS_DIR):
    """Generate a heatmap image for a single month bucket."""
    days = month_bucket.days
    if not days:
        return None

    matrix, weeks = _build_calendar_matrix(days)
    month_label = month_map.get(month_bucket.month, str(month_bucket.month))
    year = days[0].dt.year

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{month_label}-{year}.png"
    outfile = output_dir / filename

    render_calendar_heatmap(matrix, weeks, outfile)

    return {
        "month": month_label,
        "year": year,
        "image_url": f"/outputs/{filename}",
    }


def generate_calendar_heatmaps(months_cleaned, output_dir=OUTPUTS_DIR):
    """Generate heatmaps for each month and return metadata for the images."""
    heatmaps = []
    for month_bucket in months_cleaned:
        result = generate_calendar_heatmap(month_bucket, output_dir=output_dir)
        if result:
            heatmaps.append(result)
    return heatmaps


def _build_calendar_matrix(days):
    year, month = days[0].dt.year, days[0].dt.month
    offset, num_days = calendar.monthrange(year, month)

    weeks = (num_days + offset + 6) // 7
    matrix = [[np.nan for _ in range(weeks)] for _ in range(7)]

    for day in days:
        day_of_month = day.dt.day
        weekday = day.dt.weekday()
        week = (day_of_month + offset - 1) // 7
        matrix[weekday][week] = day.day_score

    return matrix, weeks

def render_calendar_heatmap(matrix, weeks, outfile):
    plt.rcParams["font.family"] = "Helvetica"
    array = np.array(matrix, dtype=float)
    fig, ax = plt.subplots(figsize=(weeks * 0.2 + 2, 3))

    # --- Colormap ---
    cmap = plt.cm.YlGn
    norm = colors.Normalize(vmin=0, vmax=10)

    # --- Draw heatmap ---
    im = ax.imshow(array, aspect="auto", interpolation="nearest", cmap=cmap, norm=norm)

    # --- Grid styling ---
    ax.set_xticks(np.arange(array.shape[1]) - 0.5, minor=True)
    ax.set_yticks(np.arange(array.shape[0]) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)

    # --- Axis labels ---
    ax.set_yticks(range(7))
    ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    ax.set_xlabel("Week", fontsize=10)
    ax.set_ylabel("Day of Week", fontsize=10)

    # --- Title ---
    ax.set_title("Weekly Day Scores", fontsize=12, pad=10, weight="bold")

    # --- Colorbar ---
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel("Day Score (0–10)", rotation=270, labelpad=15, fontsize=9)
    cbar.outline.set_visible(False)

    # --- Cleanup & save ---
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)
