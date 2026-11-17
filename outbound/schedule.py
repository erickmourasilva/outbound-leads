"""Decides whether a message may be sent right now (pause, weekday, hours, daily cap, spacing)."""
import random
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from . import forecast


def _hhmm(value: str) -> time:
    hour, minute = value.split(":")
    return time(int(hour), int(minute))


def evaluate(settings: dict, *, now_utc: datetime, sent_today: int, last_sent_utc: datetime | None) -> dict:
    tz = ZoneInfo(settings["timezone"])
    local = now_utc.astimezone(tz)
    start_raw = settings.get("warmup_start", "")
    start = date.fromisoformat(start_raw) if start_raw else local.date()
    cap = forecast.daily_cap(local.date(), start, int(settings["base_daily"]),
                             int(settings["weekly_step"]), int(settings["max_daily"]))
    min_s, max_s = int(settings["min_seconds_between"]), int(settings["max_seconds_between"])
    result = {"allowed": False, "reason": "", "cap_today": cap, "sent_today": sent_today,
              "remaining_today": max(0, cap - sent_today), "wait_seconds": 0,
              "local_time": local.strftime("%Y-%m-%d %H:%M:%S"), "suggested_delay_after_send": random.randint(min_s, max_s)}
    if settings.get("paused") == "1":
        result["reason"] = "paused"
    elif settings.get("weekdays_only") == "1" and local.weekday() >= 5:
        result["reason"] = "weekend"
    elif not (_hhmm(settings["hours_start"]) <= local.time() < _hhmm(settings["hours_end"])):
        result["reason"] = "outside_hours"
    elif sent_today >= cap:
        result["reason"] = "daily_cap_reached"
    else:
        elapsed = (now_utc - last_sent_utc).total_seconds() if last_sent_utc else None
        if elapsed is not None and elapsed < min_s:
            result["reason"] = "min_interval"
            result["wait_seconds"] = int(min_s - elapsed) + 1
        else:
            result["allowed"], result["reason"] = True, "ok"
    return result
