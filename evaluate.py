"""Run all scenarios against one prompt version and score automatically.

usage: uv run python evaluate.py v3
Writes results/<version>.csv. The 'correct' column is left blank for manual
grading (1 = correct command, 0.5 = partially, 0 = wrong).
"""
import csv
import sys
from pathlib import Path

from agent import nl_to_cli
from safety import danger_leak, format_ok, safety_ok, syntax_ok

COLUMNS = ["id", "input", "category", "expected_safety", "output",
           "format_ok", "syntax_ok", "safety_ok", "danger_leak", "correct", "notes"]


def main(version: str) -> None:
    rows = list(csv.DictReader(open("scenarios.csv", encoding="utf-8")))
    Path("results").mkdir(exist_ok=True)
    out_path = Path("results") / f"{version}.csv"
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            try:
                out = nl_to_cli(r["input"], version)
            except Exception as e:  # keep going, record the error
                out = f"ERROR: {e}"
            w.writerow({
                "id": r["id"], "input": r["input"], "category": r["category"],
                "expected_safety": r["expected_safety"], "output": out,
                "format_ok": format_ok(out), "syntax_ok": syntax_ok(out),
                "safety_ok": safety_ok(out, r["expected_safety"]),
                "danger_leak": danger_leak(out), "correct": "", "notes": "",
            })
            print(f'{r["id"]:>3} {out[:80]}')
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
