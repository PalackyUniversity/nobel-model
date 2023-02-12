from datetime import datetime, timedelta
import os

DATA_FOLDER = "data"
VACCINATION_FILE = os.path.join(DATA_FOLDER, "vaccination.csv")
DEATHS_FILE = os.path.join(DATA_FOLDER, "deaths.csv")
COUNTS_FILE = os.path.join(DATA_FOLDER, "counts.csv")

MAX_AGE = 129

AGE_CATEGORIES = [
    (0, 29),
    (30, 39),
    (40, 49),
    (50, 59),
    (60, 69),
    (70, 79),
    (80, MAX_AGE)
]


def increment_weeks(date: str, n: int = 2):
    date = datetime.strptime(date + "-1", "%Y-W%W-%w") + timedelta(weeks=n)
    date = date.isocalendar()
    return f"{date.year}-W{date.week:02d}"
