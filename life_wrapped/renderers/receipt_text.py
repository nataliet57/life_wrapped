from life_wrapped.stats import HighlightsSummary, monthly_summary

def retrieve_results(months, timeRangeSlug, domNumber, domPeriod):
    for m in months:
        print(f"month {m.month}")
        print(render_receipt(monthly_summary(m)))

def render_receipt(summary: HighlightsSummary) -> str:
    lines = []
    lines.append("          LIFE RECEIPT          ")
    lines.append("--------------------------------")
    lines.append(f"Month:       {summary.month_name}")
    lines.append(f"Days logged: {summary.days_logged:>5}")
    lines.append(f"Best day:    {summary.best_day.dt} ({summary.best_day.day_score})")
    lines.append(f"Worst day:   {summary.worst_day.dt} ({summary.worst_day.day_score})")
    lines.append(f"Avg score:   {summary.average_score:.2f}")
    lines.append(f"Sleep > avg: {summary.number_of_days_with_above_average_sleep}")
    lines.append("--------------------------------")
    return "\n".join(lines)


