import time
from datetime import datetime, timedelta


def evaluate_day_night(start_at, end_at, date_fmt, time_fmt):
    now = datetime.now()
    current_start = datetime.strptime(now.strftime(
        date_fmt) + start_at, date_fmt + time_fmt)
    delta_interval = datetime.strptime(now.strftime(
        date_fmt) + end_at, date_fmt + time_fmt) - current_start

    if delta_interval.days < 0:
        delta_interval = timedelta(
            days=0, seconds=delta_interval.seconds, microseconds=delta_interval.microseconds)

    current_end = current_start + delta_interval
    last_start = current_start + timedelta(days=-1)
    last_end = current_end + timedelta(days=-1)

    return current_start <= now <= current_end or last_start <= now <= last_end
