import calendar
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DayRecord:
    dt: datetime
    day_score: float
    highlight: str
    sleep: float
    movement: float 
    spiritual: float

@dataclass
class MonthBucket:
    year: int
    month: int
    days: list[DayRecord]

month_map = {i: calendar.month_name[i] for i in range(1, 13)}
