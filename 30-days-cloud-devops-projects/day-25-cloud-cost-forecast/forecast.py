"""Project month-end cost using the observed daily average."""
import json
import sys


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    costs = data["daily_costs"]
    assert 0 < len(costs) <= data["days_in_month"] and all(value >= 0 for value in costs)
    spent = sum(costs)
    projected = spent / len(costs) * data["days_in_month"]
    over = projected > data["budget"]
    print(f"Spent: {data['currency']} {spent:.2f} in {len(costs)} days")
    print(f"Projected: {data['currency']} {projected:.2f}; budget: {data['currency']} {data['budget']:.2f}")
    print(f"Decision: {'INVESTIGATE OVERSPEND' if over else 'WITHIN BUDGET FORECAST'}")
    return int(over)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "costs.json"))
