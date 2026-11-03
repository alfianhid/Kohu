"""Regression proof: Spark drafts must cite the pinned E12 pointer.

The extractive draft pinpoints seeded conflict side B to
``Q3-Growth!E12``. Before this fix, Spark drafting validated against
the unpinned chunk pointers, so a model echo of the containing window
``Q3-Growth!A2:F21`` passed validation and reached final claims.

Deterministic and offline: a fake Spark transport echoes whatever
licensed-market pointer appears in its prompt (scenario 1) or insists
on the window pointer (scenario 2). Either way the claims handed to
the verifier must cite ``Q3-Growth!E12``.

Usage:
  python api/verify_spark_pin.py
Exit 0 iff all checks pass. No database or network needed.
"""

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import app as askapp  # noqa: E402
import retrieval  # noqa: E402

WINDOW = "Q3-Growth!A2:F21"
PINNED = "Q3-Growth!E12"


def _check(name, cond, detail=""):
    cond = bool(cond)
    print(("PASS " if cond else "FAIL ") + name
          + ((" — " + detail) if detail and not cond else ""))
    return cond


def _fake_chunks():
    rows = ["Product X | Region | Q1 | Q2 | Q3 | Q4"]
    for row in range(2, 22):
        q3 = "7.1" if row == 12 else "1.0"
        rows.append("Product X | R%d | 1.0 | 2.0 | %s | 3.0" % (row, q3))
    return [
        {"chunk_id": "sales-7", "source_id": "sales-deck",
         "text": "Sales deck slide seven states Q3 growth 9.4 percent.",
         "citation": {"source_id": "sales-deck", "pointer": "slide 7"},
         "score": 8},
        {"chunk_id": "licensed-window", "source_id": "licensed-market",
         "text": "\n".join(rows),
         "citation": {"source_id": "licensed-market", "pointer": WINDOW},
         "score": 26},
    ]


def _licensed_pointer(claims):
    for claim in claims or []:
        if claim["citation"]["source_id"] == "licensed-market":
            return claim["citation"]["pointer"]
    return None


def main():
    manifest = retrieval.load_manifest(str(HERE.parent / "corpus"))
    draft_chunks, draft = askapp._build_draft_chunks(
        _fake_chunks(), manifest)
    ok = True
    ok &= _check("extractive draft already pinpoints side B to E12",
                 _licensed_pointer(draft) == PINNED,
                 "draft=%s" % (draft,))

    spark = askapp.SparkSynthesizer(force_off=True)
    spark.enabled = True

    def echo_pointer(prompt):
        m = re.search(r"\[licensed-market (\S+)\]", prompt)
        pointer = m.group(1) if m else WINDOW
        return json.dumps([{
            "text": "Licensed sheet Q3 growth for Product X was "
                    "7.1 percent.",
            "source_id": "licensed-market", "pointer": pointer}])

    spark._call = echo_pointer
    claims, drafted, _failed = askapp._draft_with_spark_or_extractive(
        spark, "What was Q3 growth for product X?", draft_chunks, draft)
    ok &= _check("Spark echo draft cites E12, not the containing window",
                 drafted and _licensed_pointer(claims) == PINNED,
                 "claims=%s" % (claims,))

    def stubborn_window(_prompt):
        return json.dumps([{
            "text": "Licensed sheet Q3 growth for Product X was "
                    "7.1 percent.",
            "source_id": "licensed-market", "pointer": WINDOW}])

    spark._call = stubborn_window
    claims, drafted, failed = askapp._draft_with_spark_or_extractive(
        spark, "What was Q3 growth for product X?", draft_chunks, draft)
    ok &= _check("window-only Spark draft falls back to pinned draft",
                 not drafted and failed
                 and _licensed_pointer(claims) == PINNED,
                 "claims=%s drafted=%s failed=%s"
                 % (claims, drafted, failed))

    def omit_licensed(_prompt):
        return json.dumps([{
            "text": "Sales deck slide seven states Q3 growth "
                    "9.4 percent.",
            "source_id": "sales-deck", "pointer": "slide 7"}])

    spark._call = omit_licensed
    claims, drafted, _failed = askapp._draft_with_spark_or_extractive(
        spark, "What was Q3 growth for product X?", draft_chunks, draft)
    sales = [c for c in claims
             if c["citation"]["source_id"] == "sales-deck"]
    ok &= _check("Spark omission is supplemented by pinned draft claim",
                 drafted and _licensed_pointer(claims) == PINNED
                 and len(sales) == 1,
                 "claims=%s" % (claims,))

    print("SPARK PIN VERIFY: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
