"""Verify P13: cell reads return the expected ranges."""
import json
import sys
import zipfile

from openpyxl import load_workbook

results = []


def check(name, cond, detail=""):
    results.append(cond)
    print(("PASS" if cond else "FAIL"), "-", name, detail)


manifest = json.load(open("corpus/manifest.json", encoding="utf-8"))
entries = {e["id"]: e for e in manifest["entries"]}

lm = load_workbook("corpus/licensed-market.xlsx")
pf = load_workbook("corpus/performance.xlsx")

ws = lm["Q3-Growth"]
check("licensed sheet name==manifest", "Q3-Growth" in lm.sheetnames, str(lm.sheetnames))
check("licensed range A1:F200 addressable",
      ws.max_row >= 200 and ws.max_column >= 6,
      "max_row=%d max_col=%d" % (ws.max_row, ws.max_column))
check("licensed header row", [ws.cell(1, c).value for c in range(1, 7)] ==
      ["Product", "Region", "Q1 Growth %", "Q2 Growth %", "Q3 Growth %", "Q4 Growth %"])
e12 = ws["E12"].value
check("conflict cell E12==7.1", e12 == 7.1, repr(e12))
check("conflict range matches manifest",
      entries["licensed-market"]["citation_anchors"]["conflict_range"] == "E12")

sm = pf["Summary"]
check("performance sheet name==manifest", "Summary" in pf.sheetnames, str(pf.sheetnames))
check("performance range A1:E50 addressable",
      sm.max_row >= 50 and sm.max_column >= 5,
      "max_row=%d max_col=%d" % (sm.max_row, sm.max_column))
check("performance header row", [sm.cell(1, c).value for c in range(1, 6)] ==
      ["Team", "Metric", "Q2", "Q3", "Trend"])
check("performance sample cell B2", sm["B2"].value is not None, repr(sm["B2"].value))

for f in ("corpus/licensed-market.xlsx", "corpus/performance.xlsx"):
    raw = b"".join(z.read(n) for z in [zipfile.ZipFile(f)] for n in z.namelist()
                   if n.endswith(".xml"))
    check("marker greppable in %s" % f.split("/")[1], "DEMO DATA".encode() in raw)

print()
print("ALL PASS" if all(results) else "SOME FAILED")
sys.exit(0 if all(results) else 1)
