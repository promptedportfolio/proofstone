"""Keep the owner's private research out of this public repository.

Proofstone's principle "Nothing private comes in" (README.md): no data, results, or account details
from the owner's private research enter this repository. This blocks a commit that adds:

1. a number on the owner's deny-list, which is kept outside every repository
   (~/.config/strategy-research/denylist.txt, or $STRATEGY_RESEARCH_DENYLIST): one value a line;
2. a dollar amount on a line that speaks of the owner's accounts;
3. one of the private research's own files: a playbook, a trade log, a transcript, or anything
   under data/raw/, data/series/ or results/;
4. a data file, such as a CSV, a spreadsheet or an archive, outside a samples/, examples/ or
   fixtures/ directory, where only simulated or public-domain data belongs.

A line containing `privacy-check: allow` is skipped for checks 1 and 2. Files git ignores are never
checked, since they can't be committed. Without the deny-list, check 1 is skipped with a warning.

    python3 scripts/check_private.py --staged   # the git pre-commit hook (.githooks/pre-commit)
    python3 scripts/check_private.py --all      # every tracked file
"""

import os
import re
import subprocess
import sys
from pathlib import Path

DENYLIST = Path(os.environ.get("STRATEGY_RESEARCH_DENYLIST", "~/.config/strategy-research/denylist.txt")).expanduser()
TOLERANCE = 0.005  # a rounded mention, such as $12.3k for 12,345, still matches
ALLOW = "privacy-check: allow"
PRIVATE = [re.compile(p) for p in (
    r"(^|/)PLAYBOOK[^/]*\.md$", r"(^|/)TRADE_LOG", r"(^|/)TRANSCRIPT[^/]*\.md$",
    r"(^|/)data/raw/", r"(^|/)data/series(/|$)", r"(^|/)results/")]
DATA = re.compile(r"\.(csv|tsv|xlsx|xlsm|xls|parquet|feather|arrow|h5|hdf5|pkl|pickle|db|sqlite3?|7z|zip|gz|bz2|xz)$", re.IGNORECASE)
DATA_HOME = re.compile(r"(^|/)(samples|examples|fixtures)/")
MONEY = re.compile(r"\$\s?(?P<d>\d[\d,]*(?:\.\d+)?)\s?(?P<du>k|m|million|thousand)?\b"
                   r"|\b(?P<c>\d{1,3}(?:,\d{3})+)(?![\d.])"
                   r"|\b(?P<k>\d+(?:\.\d+)?)\s?(?P<ku>k)\b", re.IGNORECASE)
ACCOUNT = re.compile(r"\b(?:my|owner'?s|owner’s)\s+(?:own\s+)?(?:taxable\s+account|ira|accounts?|portfolio|money)\b"
                     r"|\baccount (?:value|size|balance)s?\b", re.IGNORECASE)
SCALE = {"k": 1e3, "thousand": 1e3, "m": 1e6, "million": 1e6}


def amounts(line: str) -> list[float]:
    """The money-like numbers on a line: dollar amounts, comma-grouped numbers and amounts in k."""
    out = []
    for m in MONEY.finditer(line):
        if m["d"] is not None:
            digits, unit = m["d"].replace(",", ""), (m["du"] or "").lower()
        elif m["c"] is not None:
            digits, unit = m["c"].replace(",", ""), ""
        else:
            digits, unit = m["k"], "k"
        try:
            out.append(float(digits) * SCALE.get(unit, 1.0))
        except ValueError:
            continue
    return out


def denied(path: Path = DENYLIST) -> list[float] | None:
    """The deny-list's values, or None when the file isn't there."""
    if not path.exists():
        return None
    values = []
    for raw in path.read_text().splitlines():
        raw = raw.split("#")[0].strip().replace(",", "").replace("$", "")
        if raw:
            values.append(float(raw))
    return values


def check_line(line: str, deny: list[float]) -> str | None:
    """Why a line can't be committed, or None."""
    if ALLOW in line:
        return None
    found = amounts(line)
    for x in found:
        for v in deny:
            if abs(x - v) <= max(0.5, TOLERANCE * v):
                return f"a number on the deny-list ({x:,.0f})"
    if ACCOUNT.search(line) and any(x >= 1_000 for x in found):
        return "a dollar amount beside the owner's accounts"
    return None


def check_path(path: str) -> str | None:
    if any(p.search(path) for p in PRIVATE):
        return "one of the private research's files"
    if DATA.search(path) and not DATA_HOME.search(path):
        return "a data file outside samples/, examples/ or fixtures/"
    return None


def check_text(text: str, path: str, deny: list[float]) -> list[str]:
    problems = []
    if (why := check_path(path)) is not None:
        problems.append(f"{path}: {why}")
    for n, line in enumerate(text.splitlines(), 1):
        if (why := check_line(line, deny)) is not None:
            problems.append(f"{path}:{n}: {why}: {line.strip()[:120]}")
    return problems


def git(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def staged(root: Path, deny: list[float]) -> list[str]:
    """The staged paths, and every line the staged changes add."""
    problems = [f"{p}: {why}" for p in git("diff", "--cached", "--name-only", "--diff-filter=ACMR", cwd=root).splitlines()
                if (why := check_path(p)) is not None]
    path, n = None, 0
    for line in git("diff", "--cached", "-U0", "--no-color", cwd=root).splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            n = int(re.search(r"\+(\d+)", line)[1]) - 1
        elif line.startswith("+") and path is not None:
            n += 1
            if (why := check_line(line[1:], deny)) is not None:
                problems.append(f"{path}:{n}: {why}: {line[1:].strip()[:120]}")
    return problems


def tracked(root: Path, deny: list[float]) -> list[str]:
    problems = []
    for p in git("ls-files", cwd=root).splitlines():
        f = root / p
        if not f.is_file() or f.stat().st_size > 5_000_000:
            problems += [f"{p}: {why}"] if (why := check_path(p)) is not None else []
            continue
        try:
            text = f.read_text()
        except UnicodeDecodeError:
            problems += [f"{p}: {why}"] if (why := check_path(p)) is not None else []
            continue
        problems += check_text(text, p, deny)
    return problems


def main(args: list[str]) -> int:
    root = Path(git("rev-parse", "--show-toplevel").strip())
    deny = denied()
    if deny is None:
        print(f"Warning: no deny-list at {DENYLIST}, so its numbers weren't checked.", file=sys.stderr)
        deny = []
    if args == ["--staged"]:
        problems = staged(root, deny)
    elif args == ["--all"]:
        problems = tracked(root, deny)
    else:
        print(__doc__)
        return 2
    if problems:
        print("Nothing private comes into this repository (README.md, Principles). Blocked:", *problems,
              f"Fix them, or mark a line `{ALLOW}` if it holds nothing private.", sep="\n  ", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
