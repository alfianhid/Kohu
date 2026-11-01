"""Build the 2 demo spreadsheets for P13 (all content fictional).

Outputs:
  corpus/licensed-market.xlsx  sheet Q3-Growth, A1:F200 addressable;
                               D12 = 7.1 (seeded conflict vs sales deck 9.4%)
  corpus/performance.xlsx      sheet Summary, A1:E50 addressable (manager-restricted)
Each file has a Cover sheet stamped DEMO DATA - FICTIONAL with its license label.
Run:  python corpus/build_sheets.py
"""
import os

from openpyxl import Workbook
from openpyxl.styles import Font

MARKER = "DEMO DATA \u2014 FICTIONAL"
HERE = os.path.dirname(os.path.abspath(__file__))
REGIONS = ["Atlas", "Beacon", "Cobalt", "Dune"]
PRODUCTS = ["Product X", "Product Y", "Product Z"]


def cover(wb, title, license_label):
    ws = wb.active
    ws.title = "Cover"
    ws["A1"] = MARKER
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = title
    ws["A3"] = "License class: %s" % license_label
    ws["A4"] = "All vendors, teams, and figures are fictional demo data."
    ws.column_dimensions["A"].width = 60


def build_licensed_market(path):
    wb = Workbook()
    cover(wb, "Licensed market dataset (demo)", "licensed — Analyst/Steward only")
    ws = wb.create_sheet("Q3-Growth")
    ws.append(["Product", "Region", "Q1 Growth %", "Q2 Growth %", "Q3 Growth %", "Q4 Growth %"])
    # Rows 2..200: fictional data. Row 12 is the Product X rollup (conflict cell D12=7.1).
    for r in range(2, 201):
        if r == 12:
            ws.append(["Product X", "All regions", 4.1, 6.2, 7.1, 8.0])
        else:
            p = PRODUCTS[(r - 2) % 3]
            g = REGIONS[(r - 2) % 4]
            base = 2.0 + ((r * 7) % 60) / 10.0
            ws.append([p, g, round(base, 1), round(base + 1.1, 1),
                       round(base + 2.0, 1), round(base + 2.6, 1)])
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 14
    for c in "CDEF":
        ws.column_dimensions[c].width = 14
    ws.freeze_panes = "A2"
    wb.save(path)


def build_performance(path):
    wb = Workbook()
    cover(wb, "Team performance summary (demo)", "manager-restricted — Manager/Steward only")
    ws = wb.create_sheet("Summary")
    ws.append(["Team", "Metric", "Q2", "Q3", "Trend"])
    metrics = ["Deals closed", "Median close (days)", "Satisfaction /5", "Search min/query"]
    vals = {("Deals closed", "Q2"): [41, 38, 35, 29], ("Deals closed", "Q3"): [47, 44, 39, 33],
            ("Median close (days)", "Q2"): [22, 25, 28, 34], ("Median close (days)", "Q3"): [19, 22, 25, 30],
            ("Satisfaction /5", "Q2"): [4.2, 4.0, 4.1, 3.8], ("Satisfaction /5", "Q3"): [4.4, 4.3, 4.2, 4.0],
            ("Search min/query", "Q2"): [15, 16, 14, 18], ("Search min/query", "Q3"): [11, 12, 10, 13]}
    teams = ["Atlas", "Beacon", "Cobalt", "Dune"]
    r = 2
    while r <= 50:
        for m in metrics:
            for t in teams:
                if r > 50:
                    break
                q2 = vals[(m, "Q2")][teams.index(t)]
                q3 = vals[(m, "Q3")][teams.index(t)]
                trend = "up" if (q3 > q2) != m.startswith("Median") and m != "Search min/query" else ("down" if q3 < q2 else "flat")
                if m in ("Median close (days)", "Search min/query"):
                    trend = "down-good" if q3 < q2 else "flat"
                ws.append([t, m, q2, q3, trend])
                r += 1
    for c, w in zip("ABCDE", (12, 22, 10, 10, 12)):
        ws.column_dimensions[c].width = w
    ws.freeze_panes = "A2"
    wb.save(path)


if __name__ == "__main__":
    build_licensed_market(os.path.join(HERE, "licensed-market.xlsx"))
    build_performance(os.path.join(HERE, "performance.xlsx"))
    print("wrote licensed-market.xlsx (Q3-Growth A1:F200, D12=7.1) and performance.xlsx (Summary A1:E50)")
