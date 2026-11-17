import unittest
from datetime import date

from outbound import forecast

SETTINGS = {"timezone": "America/Sao_Paulo", "warmup_start": "2026-11-23", "base_daily": "5",
            "weekly_step": "5", "max_daily": "30", "weekdays_only": "1"}


class ForecastTest(unittest.TestCase):
    def test_cap_grows_weekly_and_is_capped(self):
        start = date(2026, 11, 23)
        self.assertEqual(forecast.daily_cap(start, start, 5, 5, 30), 5)
        self.assertEqual(forecast.daily_cap(date(2026, 11, 30), start, 5, 5, 30), 10)
        self.assertEqual(forecast.daily_cap(date(2027, 3, 1), start, 5, 5, 30), 30)

    def test_weekends_are_skipped(self):
        # Friday 2026-11-27 with 20 leads: Fri 5, then Mon/Tue...
        plan = forecast.project(20, SETTINGS, 0, today=date(2026, 11, 27))["plan"]
        days = [date.fromisoformat(p["date"]).weekday() for p in plan]
        self.assertTrue(all(d < 5 for d in days))

    def test_queue_finishes_and_respects_caps(self):
        out = forecast.project(40, SETTINGS, 0, today=date(2026, 11, 23))
        self.assertIsNotNone(out["finish_date"])
        self.assertTrue(all(p["planned"] <= p["cap"] for p in out["plan"]))
        self.assertEqual(sum(p["planned"] for p in out["plan"]), 40)

    def test_today_already_sent_reduces_availability(self):
        out = forecast.project(10, SETTINGS, 5, today=date(2026, 11, 23))
        self.assertEqual(out["plan"][0]["planned"], 0)

    def test_empty_queue(self):
        out = forecast.project(0, SETTINGS, 0, today=date(2026, 11, 23))
        self.assertEqual(out["remaining"], 0)
        self.assertIsNone(out["finish_date"])


if __name__ == "__main__":
    unittest.main()
