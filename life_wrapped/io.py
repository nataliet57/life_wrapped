import pandas as pd
from .models import DayRecord

COLMAP = {
    "how would you rate your day?": "day_score",
    "how much sleep did you get": "sleep",
    "was i able to get some movement in my day": "movement",
    "did you spend time with god?": "spiritual",
    "date": "date",
}

REQUIRED_COLS = ["date", "sleep", "day_score", "highlight"]

def load_days_from_excel(path: str) -> list[DayRecord]:
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns=COLMAP)

    # missing_rows = df[df[REQUIRED_COLS].isna().any(axis=1)]

    # # validate required columns are present
    # if not missing_rows.empty:
    #     raise Exception(f"missing rows {missing_rows}")
    df = df.dropna(subset=REQUIRED_COLS)
    
    # coerce type
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["highlight"] = df["highlight"].astype("string")
    df["day_score"] = df["day_score"].astype(float)

    days: list[DayRecord] = []

    # create a new day record
    for idx, row in df.iterrows():
        day = DayRecord(
            dt= row['date'],
            day_score = row['day_score'],
            highlight = row['highlight'],
            sleep = row['sleep'],
            movement = row['movement'],
            spiritual = row['spiritual']
        )
        days.append(day)
    return days