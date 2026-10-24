"""Tests for check_private.py, using the standard library only: python3 -m unittest discover scripts"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_private as cp  # noqa: E402

DENY = [12_345.0, 67_890.0]  # made-up values, not the owner's


class Lines(unittest.TestCase):
    def test_a_deny_listed_number_is_blocked_in_any_form(self):
        for line in ("It holds $12,345.", "about 12,345 in all", "roughly $12.3k", "12.35k"):
            self.assertIsNotNone(cp.check_line(line, DENY), line)

    def test_other_numbers_pass(self):
        for line in ("1,000 tests tried", "t-statistic 1.96", "$5 a month", "about 3.5 MB"):
            self.assertIsNone(cp.check_line(line, DENY), line)

    def test_a_dollar_amount_beside_the_owners_accounts_is_blocked(self):
        self.assertIsNotNone(cp.check_line("The owner's IRA holds $4,321,000.", []))  # privacy-check: allow (a made-up amount that tests this rule)
        self.assertIsNone(cp.check_line("A $4,321,000 example account.", []))

    def test_the_allow_marker_skips_a_line(self):
        self.assertIsNone(cp.check_line("$12,345 is a made-up example. privacy-check: allow", DENY))


class Paths(unittest.TestCase):
    def test_the_private_researchs_files_are_blocked(self):
        for path in ("PLAYBOOK.md", "notes/PLAYBOOK-2026-10-24.md", "TRADE_LOG.md", "TRANSCRIPT.md",
                     "study/data/raw/x.json", "study/data/series/x", "results/report.md"):
            self.assertIsNotNone(cp.check_path(path), path)

    def test_data_files_belong_in_samples_examples_or_fixtures(self):
        for path in ("returns.csv", "src/proofstone/chain.parquet", "chains.7z", "book.xlsx"):
            self.assertIsNotNone(cp.check_path(path), path)
        for path in ("samples/simulated.csv", "examples/fred/DGS3MO.csv", "tests/fixtures/run.xlsx", "README.md"):
            self.assertIsNone(cp.check_path(path), path)


class DenyList(unittest.TestCase):
    def test_a_missing_deny_list_is_none_and_comments_are_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(cp.denied(Path(d) / "missing.txt"))
            f = Path(d) / "denylist.txt"
            f.write_text("# made-up values\n$12,345\n67890  # another\n\n")
            self.assertEqual(cp.denied(f), DENY)


class Staged(unittest.TestCase):
    def test_only_the_lines_a_commit_adds_are_checked(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            run = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True)
            run("init", "-q")
            (root / "plan.md").write_text("old line, $12,345\n")
            run("add", "plan.md")
            run("-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", "commit", "-qm", "x")
            (root / "plan.md").write_text("old line, $12,345\nnew line\n")
            (root / "data.csv").write_text("a,b\n")
            run("add", "plan.md", "data.csv")
            problems = cp.staged(root, DENY)
            self.assertEqual(len(problems), 1)
            self.assertIn("data.csv", problems[0])
            (root / "plan.md").write_text("old line, $12,345\nnew line, 67,890\n")
            run("add", "plan.md")
            self.assertTrue(any("plan.md:2" in p for p in cp.staged(root, DENY)))


if __name__ == "__main__":
    unittest.main()
