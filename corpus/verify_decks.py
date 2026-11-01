"""Verify P12: slide counts match manifest + conflict figure present."""
import json
import sys

from pptx import Presentation


def text_of(slide):
    return "\n".join(s.text for s in slide.shapes if s.has_text_frame)


results = []


def check(name, cond, detail=""):
    results.append(cond)
    print(("PASS" if cond else "FAIL"), "-", name, detail)


manifest = json.load(open("corpus/manifest.json", encoding="utf-8"))
entries = {e["id"]: e for e in manifest["entries"]}
prod = Presentation("corpus/product-deck.pptx")
sales = Presentation("corpus/sales-deck.pptx")

check("product-deck slides==manifest(10)",
      len(prod.slides) == len(entries["product-deck"]["citation_anchors"]["slides"]) == 10,
      str(len(prod.slides)))
check("sales-deck slides==manifest(8)",
      len(sales.slides) == len(entries["sales-deck"]["citation_anchors"]["slides"]) == 8,
      str(len(sales.slides)))
check("marker on all 10 product slides",
      sum(1 for s in prod.slides if "DEMO DATA" in text_of(s)) == 10)
check("marker on all 8 sales slides",
      sum(1 for s in sales.slides if "DEMO DATA" in text_of(s)) == 8)
check("stable numbers on product deck",
      all("Slide %d of 10" % (i + 1) in text_of(s) for i, s in enumerate(prod.slides)))
check("stable numbers on sales deck",
      all("Slide %d of 8" % (i + 1) in text_of(s) for i, s in enumerate(sales.slides)))

cs = entries["sales-deck"]["citation_anchors"]["conflict_slide"]
s7 = text_of(sales.slides[cs - 1])
check("conflict slide %d holds 9.4%% deck figure" % cs, "9.4" in s7)
check("conflict figure differs from licensed sheet 7.1%",
      "9.4" in s7 and manifest["conflict_pair"]["side_b"]["claim"].startswith("Q3 growth") and "7.1" in manifest["conflict_pair"]["side_b"]["claim"])
check("sales slide 7 has embedded chart",
      any(s.has_chart for s in sales.slides[cs - 1].shapes))

print()
print("ALL PASS" if all(results) else "SOME FAILED")
sys.exit(0 if all(results) else 1)
