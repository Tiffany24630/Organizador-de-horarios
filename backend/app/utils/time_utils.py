from datetime import datetime
from datetime import timedelta

def str_to_time(value: str):
    return datetime.strptime(value, "%H:%M").time()

def add_minutes(value: str, minutes: int):
    dt = datetime.strptime(value, "%H:%M")
    dt += timedelta(minutes=minutes)

    return dt.strftime("%H:%M")

def minutes_between(start, end):
    start_dt = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)

    return int((end_dt - start_dt).total_seconds() / 60)