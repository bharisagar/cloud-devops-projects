"""Verify a release payload against its expected SHA-256 digest."""
import hashlib
import json
import sys
from pathlib import Path


def main(payload_path, manifest_path):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    actual = hashlib.sha256(Path(payload_path).read_bytes()).hexdigest()
    expected = manifest["sha256"].lower()
    match = actual == expected
    print(f"Expected: {expected}\nActual:   {actual}\nDecision: {'MATCH' if match else 'MISMATCH'}")
    return int(not match)


if __name__ == "__main__":
    sys.exit(main(*(sys.argv[1:] or ["payload.txt", "manifest.json"])))
