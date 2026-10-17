"""Compare a few explicitly governed workload properties."""
import json
import sys


def main(desired_path, observed_path):
    desired = json.load(open(desired_path, encoding="utf-8"))
    observed = json.load(open(observed_path, encoding="utf-8"))
    drift = [(key, desired.get(key), observed.get(key)) for key in ("name", "image", "replicas", "environment") if desired.get(key) != observed.get(key)]
    for key, expected, actual in drift:
        print(f"DRIFT {key}: desired={expected!r}, observed={actual!r}")
    print(f"Decision: {'REVIEW' if drift else 'IN SYNC'}")
    return int(bool(drift))


if __name__ == "__main__":
    sys.exit(main(*(sys.argv[1:] or ["desired.json", "observed.json"])))
