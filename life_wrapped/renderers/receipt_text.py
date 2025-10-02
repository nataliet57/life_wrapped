"""Console receipt renderer for monthly summaries."""
from __future__ import annotations

from typing import Iterable, Dict, Any

from life_wrapped.stats import monthly_summary


def retrieve_results(months_cleaned: Iterable, *_args) -> None:
    for bucket in months_cleaned:
        summary = monthly_summary(bucket)
        print(render_receipt(summary))


def render_receipt(summary: Dict[str, Any]) -> str:
    lines = [
        "          LIFE RECEIPT          ",
        "--------------------------------",
        f"Month:       {summary.get('month_name', 'Unknown')} {summary.get('year', '')}",
        f"Days logged: {summary.get('days_logged', 0):>5}",
    ]

    worst_day = summary.get("worst_day") or {}
    lines.append(
        f"Worst day:   {worst_day.get('dt', '—')} ({worst_day.get('day_score', '—')})"
    )
    avg_score = float(summary.get("average_score", 0))
    lines.append(f"Avg score:   {avg_score:.2f}")
    lines.append(
        "Number of days where I met my sleep goal: "
        f"{summary.get('number_of_days_with_above_average_sleep', 0)}"
    )
    lines.append("--------------------------------")
    return "\n".join(lines)
