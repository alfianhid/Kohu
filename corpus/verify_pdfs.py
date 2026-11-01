"""Verify P11: text extraction finds the tables and chart captions."""
import sys

from pypdf import PdfReader

results = []


def check(name, cond, detail=""):
    results.append(cond)
    print(("PASS" if cond else "FAIL"), "-", name, detail)


h = PdfReader("corpus/handbook.pdf")
r = PdfReader("corpus/process-report.pdf")
ht = " ".join([(p.extract_text() or "") for p in h.pages])
rt = " ".join([(p.extract_text() or "") for p in r.pages])

check("handbook pages==12", len(h.pages) == 12, str(len(h.pages)))
check("report pages==9", len(r.pages) == 9, str(len(r.pages)))
check("marker on all 12 handbook pages",
      sum(1 for p in h.pages if "DEMO DATA" in (p.extract_text() or "")) == 12)
check("marker on all 9 report pages",
      sum(1 for p in r.pages if "DEMO DATA" in (p.extract_text() or "")) == 9)
check("table1 header extracts", "Time-off allowances" in ht)
check("table1 cells extract", "Tenure" in ht and "Rollover up to 5" in ht)
check("table2 header extracts", "Support hours by channel" in ht)
check("table2 cells extract", "On-call" in ht and "Duty rota" in ht)
check("figure1 caption extracts", "Figure 1" in rt and "Dune is slowest" in rt)
check("figure1 data extracts", "Cobalt" in rt and "17" in rt)
check("figure2 caption extracts", "Figure 2" in rt and "16 to 10 minutes" in rt)
check("figure2 data extracts", "Median minutes" in rt)

print()
print("ALL PASS" if all(results) else "SOME FAILED")
sys.exit(0 if all(results) else 1)
