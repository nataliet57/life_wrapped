from life_wrapped.stats import HighlightsSummary, monthly_summary

def retrieve_results(months_cleaned, timeRangeSlug, domNumber, domPeriod):
    for m in months_cleaned:
        print(f"month {m.month}")
        monthly_highlight_summary = monthly_summary(m)
        print(render_receipt(monthly_highlight_summary))

def render_receipt(summary: HighlightsSummary) -> str:
    

