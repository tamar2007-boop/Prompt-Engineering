"""Merge results/*.csv into results/results.xlsx (one sheet per iteration).
Upload the file to Google Sheets (File > Import) for submission.
Also prints an average score per metric for each iteration.
"""
import csv
from pathlib import Path

from openpyxl import Workbook

METRICS = ["format_ok", "syntax_ok", "safety_ok", "danger_leak", "correct"]

wb = Workbook()
wb.remove(wb.active)
for p in sorted(Path("results").glob("v*.csv")):
    rows = list(csv.reader(open(p, encoding="utf-8-sig")))
    ws = wb.create_sheet(p.stem)
    for r in rows:
        ws.append(r)
    header, data = rows[0], rows[1:]
    print(p.stem, end=": ")
    for m in METRICS:
        vals = [float(r[header.index(m)]) for r in data if r[header.index(m)] not in ("", None)]
        if vals:
            print(f"{m}={sum(vals)/len(vals):.2f}", end="  ")
    print()
wb.save("results/results.xlsx")
print("Saved results/results.xlsx")
