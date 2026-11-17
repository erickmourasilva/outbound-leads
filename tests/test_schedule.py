import unittest
from datetime import datetime, timedelta, timezone

from outbound import schedule

S = {"timezone": "America/Sao_Paulo", "paused": "0", "warmup_start": "2026-11-16", "base_daily": "5",
     "weekly_step": "5", "max_daily": "30", "hours_start": "09:00", "hours_end": "20:00",
     "weekdays_only": "1", "min_seconds_between": "90", "max_seconds_between": "240"}


def utc(y, m, d, hh, mm=0):
    # Sao Paulo is UTC-3
    return datetime(y, m, d, hh, mm, tzinfo=timezone.utc) + timedelta(hours=3)


class ScheduleTest(unittest.TestCase):
    def test_allowed_in_hours(self):
        r = schedule.evaluate(S, now_utc=utc(2026, 11, 17, 10), sent_today=0, last_sent_utc=None)  # Tuesday
        self.assertTrue(r["allowed"])
        self.assertEqual(r["cap_today"], 5)

    def test_paused_blocks(self):
        r = schedule.evaluate({**S, "paused": "1"}, now_utc=utc(2026, 11, 17, 10), sent_today=0, last_sent_utc=None)
        self.assertEqual(r["reason"], "paused")

    def test_weekend_blocks(self):
        r = schedule.evaluate(S, now_utc=utc(2026, 11, 21, 10), sent_today=0, last_sent_utc=None)  # Saturday
        self.assertEqual(r["reason"], "weekend")

    def test_outside_hours_blocks(self):
        for hour in (7, 20, 22):
            r = schedule.evaluate(S, now_utc=utc(2026, 11, 17, hour), sent_today=0, last_sent_utc=None)
            self.assertEqual(r["reason"], "outside_hours", hour)

    def test_daily_cap(self):
        r = schedule.evaluate(S, now_utc=utc(2026, 11, 17, 10), sent_today=5, last_sent_utc=None)
        self.assertEqual(r["reason"], "daily_cap_reached")

    def test_cap_grows_after_a_week(self):
        r = schedule.evaluate(S, now_utc=utc(2026, 11, 24, 10), sent_today=0, last_sent_utc=None)
        self.assertEqual(r["cap_today"], 10)

    def test_min_interval(self):
        now = utc(2026, 11, 17, 10)
        r = schedule.evaluate(S, now_utc=now, sent_today=1, last_sent_utc=now - timedelta(seconds=30))
        self.assertEqual(r["reason"], "min_interval")
        self.assertGreater(r["wait_seconds"], 0)
        ok = schedule.evaluate(S, now_utc=now, sent_today=1, last_sent_utc=now - timedelta(seconds=120))
        self.assertTrue(ok["allowed"])
        self.assertTrue(90 <= ok["suggested_delay_after_send"] <= 240)


if __name__ == "__main__":
    unittest.main()
