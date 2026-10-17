"""Compare source and restored records by ID and content."""
import json
import sys


def main(source_path, restored_path):
    source = json.load(open(source_path, encoding="utf-8"))
    restored = json.load(open(restored_path, encoding="utf-8"))
    assert source["dataset"] == restored["dataset"], "dataset names differ"
    original = {record["id"]: record for record in source["records"]}
    recovered = {record["id"]: record for record in restored["records"]}
    assert len(original) == len(source["records"]) and len(recovered) == len(restored["records"]), "duplicate record ID"
    match = original == recovered
    print(f"Source records: {len(original)}; restored records: {len(recovered)}")
    print(f"Decision: {'RESTORE VERIFIED' if match else 'RESTORE FAILED'}")
    return int(not match)


if __name__ == "__main__":
    sys.exit(main(*(sys.argv[1:] or ["source.json", "restored.json"])))
