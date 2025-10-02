"""Statistics helpers for life-wrapped summaries."""
from __future__ import annotations

import heapq
from typing import Iterable, Dict, Any, List

from life_wrapped.models import DayRecord, MonthBucket, month_map


def get_number_of_days_with_above_average_sleep(month: MonthBucket) -> int:
    """Counts the number of days where sleep scored above the threshold."""
    return sum(1 for d in month.days if d.sleep and d.sleep > 2)


def _serialize_day(day: DayRecord) -> Dict[str, Any]:
    return {
        "dt": day.dt.isoformat(),
        "day_score": day.day_score,
        "highlight": day.highlight,
        "sleep": day.sleep,
        "movement": day.movement,
        "spiritual": day.spiritual,
    }


def get_best_days(month: MonthBucket) -> List[Dict[str, Any]]:
    """Returns the top five days in the month ranked by score."""
    top_days = heapq.nlargest(5, month.days, key=lambda d: d.day_score)
    return [_serialize_day(day) for day in top_days]


def get_worst_days(month: MonthBucket) -> List[Dict[str, Any]]:
    """Returns the lowest scoring day in the month."""
    worst_days = heapq.nsmallest(3, month.days, key=lambda d: d.day_score)
    return [_serialize_day(day) for day in worst_days]


def get_monthly_average_score(month: MonthBucket) -> float:
    """Returns the mean score for the given month."""
    return sum(d.day_score for d in month.days) / len(month.days)



def monthly_summary(month: MonthBucket) -> Dict[str, Any]:
    """Builds a JSON-serialisable summary for the supplied month bucket."""
    summary: Dict[str, Any] = {
        "month_name": month_map.get(month.month, str(month.month)),
        "year": month.year,
        "days_logged": len(month.days),
        "top_five_days": get_best_days(month),
        "worst_day": get_worst_days(month),
        "average_score": get_monthly_average_score(month),
    }

    if any(day.sleep is not None for day in month.days):
        summary["number_of_days_with_above_average_sleep"] = (
            get_number_of_days_with_above_average_sleep(month)
        )

    return summary


def bucket_by_month(days: Iterable[DayRecord]) -> List[MonthBucket]:
    """Groups DayRecord instances by year/month."""
    month_key_hash: Dict[tuple[int, int], List[DayRecord]] = {}
    for day in days:
        key = (day.dt.year, day.dt.month)
        month_key_hash.setdefault(key, []).append(day)

    return [
        MonthBucket(year, month, sorted(records, key=lambda d: d.dt))
        for (year, month), records in sorted(month_key_hash.items())
    ]
