from dataclasses import dataclass
from collections import Counter, defaultdict
from typing import Iterable

from life_wrapped.models import DayRecord, MonthBucket, HighlightsSummary

def get_number_of_days_with_above_average_sleep(month: MonthBucket)-> int:
    return sum(1 for d in month.days if d.sleep and d.sleep > 2)

def get_best_day(month: MonthBucket) -> DayRecord:
    return max(month.days, key=lambda d:d.day_score)

def get_worst_day(month: MonthBucket) -> DayRecord:
    return min(month.days, key=lambda d:d.day_score)

def get_monthly_average_score(month: MonthBucket) -> int:
    return sum(d.day_score for d in month.days)/len(month.days)

def monthly_summary(month: MonthBucket) -> HighlightsSummary:
    # compute averages, top highlights, best/worst days
    return HighlightsSummary(
        month_name = month.month,
        days_logged = len(month.days),
        best_day = get_best_day(month),
        worst_day = get_worst_day(month),
        average_score = get_monthly_average_score(month),
        number_of_days_with_above_average_sleep = get_number_of_days_with_above_average_sleep(month),
    )

def bucket_by_month(days):
    month_key_hash = {}
    for d in days:
        k = (d.dt.year, d.dt.month)
        if k not in month_key_hash:
            month_key_hash[k] = []
        month_key_hash[(d.dt.year, d.dt.month)].append(d)

    # freeze the list
    return [
        MonthBucket(cur_year, cur_month, sorted(days, key=lambda d:d.dt))
        for (cur_year, cur_month), days in month_key_hash.items()
    ]