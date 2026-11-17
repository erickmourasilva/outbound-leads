"""Sending forecast: how many DMs per day the warm-up allows and when the queue empties."""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


def daily_cap(day: date, start: date, base: int, step: int, max_daily: int) -> int:
    weeks = max(0, (day - start).days // 7)
    return min(max_daily, base + step * weeks)


def project(remaining: int, settings: dict, sent_today: int, today: date | None = None, horizon_days: int = 400) -> dict:
    tz = ZoneInfo(settings.get("timezone", "America/Sao_Paulo"))
    today = today or datetime.now(tz).date()
    start_raw = settings.get("warmup_start", "")
    start = date.fromisoformat(start_raw) if start_raw else today
    base, step, max_daily = int(settings["base_daily"]), int(settings["weekly_step"]), int(settings["max_daily"])
    weekdays_only = settings.get("weekdays_only", "1") == "1"

    plan, left, day = [], remaining, today
    for _ in range(horizon_days):
        if left <= 0:
            break
        if weekdays_only and day.weekday() >= 5:
            day += timedelta(days=1)
            continue
        cap = daily_cap(day, start, base, step, max_daily)
        available = max(0, cap - sent_today) if day == today else cap
        n = min(left, available)
        if n > 0 or day == today:
            plan.append({"date": day.isoformat(), "cap": cap, "planned": n})
        left -= n
        day += timedelta(days=1)
    finish = plan[-1]["date"] if plan and left <= 0 else None
    return {
        "remaining": remaining,
        "today_cap": daily_cap(today, start, base, step, max_daily),
        "finish_date": finish,
        "days": len([p for p in plan if p["planned"] > 0]),
        "plan": plan[:21],
    }
