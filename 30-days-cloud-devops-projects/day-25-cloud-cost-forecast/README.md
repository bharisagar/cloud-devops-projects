# Day 25 - Cloud Cost Forecast

Forecast month-end spend from a partial month of synthetic daily cloud costs. The exercise distinguishes a forecast from an actual bill.

## Architecture

`costs.json` -> `forecast.py` -> projected total and budget check.

## Run

From this folder, run `python forecast.py costs.json`. Expect an over-budget forecast. Reduce the daily run rate in a copy and rerun. In a real account, obtain daily costs from the provider billing API, include credits and taxes where relevant, and use alerts before the budget is exhausted.

## Evidence

Capture actual spend to date, projected total, and the budget gap. Explain why a linear forecast can miss a sudden deployment or one-time purchase.

## Cleanup

No cloud resources are created.
