from life_wrapped.models import month_map
import numpy as np
import matplotlib.pyplot as plt
import os
import calendar
from matplotlib import colors
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


# Prepares the (7, W) array and tick label metadata.
def build_calendar_grid(months_cleaned):
    grids = []
    for current_month_bucket in months_cleaned:
        current_days = current_month_bucket.days
        build_7_w_array(current_days, month_map[current_month_bucket.month])

def build_7_w_array(days, month_label):
    year, month = days[0].dt.year, days[0].dt.month
    # offset = weekday of 1st day (0=Monday, 6=Sunday)
    offset, num_days = calendar.monthrange(year, month)  
    
    W = (num_days + offset + 6) // 7  # total weeks needed
    A = [[None for _ in range(W)] for _ in range(7)]
    
    for d in days:
        day_of_month = d.dt.day
        weekday = d.dt.weekday()  # 0=Mon
        week = (day_of_month + offset - 1) // 7
        A[weekday][week]= d.day_score

    os.makedirs("outputs", exist_ok=True)
    outfile = os.path.join("outputs", f"{month_label}.png")
    render_calendar_heatmap(A, W, outfile)
    return outfile

# Plots with matplotlib, adds labels, saves PNG.
def render_calendar_heatmap(A, W, outfile):
    A = np.array(A, dtype=float)
    fig, ax = plt.subplots(figsize=(W * 0.2 + 2, 3))
    plt.rcParams["font.family"] = "Helvetica"
    
    # Define custom gradient: yellow → light green → dark green
    cmap = LinearSegmentedColormap.from_list(
        "custom_green",
        [(0, "yellow"), (0.5, "lightgreen"), (1, "darkgreen")]
    )

    # Normalize values 0 → 10
    norm = colors.Normalize(vmin=0, vmax=10)

    im = ax.imshow(A, aspect='auto', interpolation='nearest', cmap=cmap, norm=norm)

    ax.set_yticks(range(7))
    ax.set_yticklabels(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.spines[:].set_visible(True)

    cbar = fig.colorbar(im, ax=ax, orientation="vertical", shrink=0.7)
    cbar.set_label("Day Score (0–10)")

    plt.tight_layout()
    fig.savefig(outfile, dpi=150)
