import contextlib
import io
import json
import math
import tempfile
import unittest
from pathlib import Path

from backtest_evidence.cli import main
from backtest_evidence.core import audit_events, check_research_dates, pnl_report
from backtest_evidence.manifest import create_manifest, verify_manifest


def rows(*values):
    return [{"date": f"2024-01-{i:02d}", "pnl": v} for i, v in enumerate(values, 1)]


class AccountingTests(unittest.TestCase):
    def test_initial_loss_is_drawdown(self):
        result = pnl_report(rows(-10, 20, -22), 100)["metrics"]
        self.assertEqual(result["total_pnl"], -12)
        self.assertEqual(result["ending_equity"], 88)
        self.assertEqual(result["max_drawdown_amount"], 22)
        self.assertAlmostEqual(result["max_drawdown_fraction"], 0.2)
        self.assertAlmostEqual(result["pnl_over_max_drawdown"], -12 / 22)
        first = pnl_report(rows(-10), 100)["metrics"]
        self.assertEqual(first["max_drawdown_amount"], 10)
        self.assertIsNone(first["sharpe_zero_rf"])

    def test_known_sharpe_uses_prior_equity(self):
        # Returns +10%, -10%: mean zero, nonzero sample deviation.
        result = pnl_report(rows(10, -11), 100)["metrics"]
        self.assertAlmostEqual(result["sharpe_zero_rf"], 0)
        self.assertAlmostEqual(result["total_return"], -0.01)

    def test_unknown_is_never_zero(self):
        for missing in (None, "", "N/A", "NA", "  "):
            with self.subTest(missing=missing):
                result = pnl_report(rows(5, missing, 0), 100)
                self.assertEqual(result["status"], "incomplete")
                self.assertIsNone(result["metrics"])
                self.assertEqual(result["zero_pnl_sessions"], 1)

    def test_omitted_session_and_unexpected_session(self):
        result = pnl_report(rows(5), 100, ["2024-01-01", "2024-01-02"])
        self.assertEqual(result["absent_sessions"], ["2024-01-02"])
        self.assertIsNone(result["metrics"])
        with self.assertRaises(ValueError):
            pnl_report(rows(5, 2), 100, ["2024-01-01"])

    def test_coverage_not_claimed_without_calendar(self):
        result = pnl_report(rows(0, 0), 100)
        self.assertFalse(result["coverage_checked"])
        self.assertIsNone(result["metrics"]["pnl_over_max_drawdown"])
        self.assertIsNone(result["metrics"]["sharpe_zero_rf"])

    def test_bad_dates_rejected(self):
        for dates in (["2024-01-01", "2024-01-01"], ["2024-01-02", "2024-01-01"], ["20240101"], ["2024-02-30"]):
            with self.subTest(dates=dates), self.assertRaises(ValueError):
                pnl_report([{"date": d, "pnl": 1} for d in dates], 100)

    def test_nonfinite_and_invalid_capital_rejected(self):
        for value in (math.nan, math.inf, -math.inf, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                pnl_report(rows(value), 100)
        for value in (0, -1, math.nan):
            with self.subTest(value=value), self.assertRaises(ValueError):
                pnl_report(rows(1), value)

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            pnl_report([], 100)

    def test_bankruptcy_reported_without_sharpe(self):
        result = pnl_report(rows(-120, 10), 100)
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["metrics"]["max_drawdown_amount"], 120)
        self.assertIsNone(result["metrics"]["sharpe_zero_rf"])


class CausalityTests(unittest.TestCase):
    def test_offsets_compared_as_instants(self):
        result = audit_events([{"available_at": "2024-01-02T09:29:59-05:00",
                                "decision_at": "2024-01-02T14:30:00Z",
                                "executed_at": "2024-01-02T14:30:01+00:00"}])
        self.assertEqual(result["status"], "ok")

    def test_future_information_and_early_execution(self):
        result = audit_events([{"available_at": "2024-01-02T15:00:00Z",
                                "decision_at": "2024-01-02T14:00:00Z",
                                "executed_at": "2024-01-02T13:00:00Z"}])
        self.assertEqual({x["code"] for x in result["findings"]},
                         {"DATA_AFTER_DECISION", "EXECUTION_BEFORE_DECISION"})

    def test_missing_or_naive_timestamp_and_empty(self):
        for data in ([{}], [{"available_at": "2024-01-02T15:00:00"}], []):
            self.assertEqual(audit_events(data)["status"], "invalid")

    def test_oos_boundary_is_exclusive(self):
        result = check_research_dates(["2024-01-01", "2024-01-02"], "2024-01-02")
        self.assertEqual(result["violating_dates"], ["2024-01-02"])


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "config.json").write_text('{"lookback": 5}')

    def test_known_sha_and_tampering(self):
        (self.root / "abc").write_bytes(b"abc")
        manifest = create_manifest(self.root, ["abc", "config.json"])
        self.assertEqual(manifest["files"]["abc"]["sha256"],
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(verify_manifest(self.root, manifest)["status"], "ok")
        (self.root / "abc").write_bytes(b"abd")
        self.assertEqual(verify_manifest(self.root, manifest)["status"], "invalid")

    def test_paths_must_stay_in_root(self):
        for name in ("../outside", "/etc/passwd", "./config.json", "a/../config.json", "a\\config.json"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                create_manifest(self.root, [name])

    def test_symlinks_rejected(self):
        try:
            (self.root / "link").symlink_to(self.root / "config.json")
        except OSError:
            self.skipTest("symlink creation unavailable")
        with self.assertRaises(ValueError):
            create_manifest(self.root, ["link"])

    def test_empty_manifest_and_removed_file_rejected(self):
        with self.assertRaises(ValueError):
            create_manifest(self.root, [])
        manifest = create_manifest(self.root, ["config.json"])
        (self.root / "config.json").unlink()
        with self.assertRaises(ValueError):
            verify_manifest(self.root, manifest)


class CLITests(unittest.TestCase):
    def test_demo_and_negative_exit_codes(self):
        for file, code, status in (("daily_pnl.csv", 0, "ok"), ("missing_pnl.csv", 2, "incomplete")):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                actual = main(["report", "examples/" + file, "--capital", "1000", "--sessions", "examples/sessions.csv"])
            self.assertEqual(actual, code)
            self.assertEqual(json.loads(out.getvalue())["status"], status)

    def test_bad_csv_has_actionable_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text("date,pnl,pnl\n2024-01-01,1,2\n")
            with contextlib.redirect_stderr(io.StringIO()) as err:
                code = main(["report", str(path), "--capital", "100"])
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(err.getvalue())["status"], "error")


if __name__ == "__main__":
    unittest.main()
