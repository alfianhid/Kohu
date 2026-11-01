"""Verify P10: manifest has 8 entries with required fields + 1 conflict pair."""
import json
import sys

manifest = json.load(open("corpus/manifest.json", encoding="utf-8"))
entries = manifest.get("entries", [])
pair = manifest.get("conflict_pair")
pairs = manifest.get("conflict_pairs", [])

n_entries = len(entries)
with_fields = sum(
    1 for e in entries
    if e.get("id") and e.get("filename")
    and (e.get("license_class") or e.get("licenseClass"))
    and (e.get("citation_anchors") or e.get("citationAnchors"))
)
n_pairs = len(pairs) if isinstance(pairs, list) else 0
pair_ok = (
    isinstance(pair, dict)
    and pair.get("side_a", {}).get("source_id") == "sales-deck"
    and "slide" in pair.get("side_a", {}).get("anchor", {})
    and pair.get("side_b", {}).get("source_id") == "licensed-market"
    and "range" in pair.get("side_b", {}).get("anchor", {})
)

print("entries: %d (with id/filename/license/citations: %d)" % (n_entries, with_fields))
print("conflict_pairs: %d, conflict_pair sales-slide-vs-sheet-range: %s" % (n_pairs, pair_ok))

ok = n_entries == 8 and with_fields == 8 and n_pairs == 1 and pair_ok
print("ASSERT 8 entries + 1 conflict pair:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
