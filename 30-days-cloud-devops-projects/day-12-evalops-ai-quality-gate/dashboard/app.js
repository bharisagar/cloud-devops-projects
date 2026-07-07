const sampleReportPath = "../reports/sample-eval-report.json";

const els = {
  upload: document.querySelector("#reportUpload"),
  score: document.querySelector("#score"),
  gate: document.querySelector("#gate"),
  decision: document.querySelector("#decision"),
  summaryLine: document.querySelector("#summaryLine"),
  totalChecks: document.querySelector("#totalChecks"),
  passed: document.querySelector("#passed"),
  partial: document.querySelector("#partial"),
  failed: document.querySelector("#failed"),
  criticalFailures: document.querySelector("#criticalFailures"),
  caseTitle: document.querySelector("#caseTitle"),
  checks: document.querySelector("#checks"),
  nextActions: document.querySelector("#nextActions"),
};

function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

function addText(parent, tag, text, className) {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  parent.appendChild(element);
  return element;
}

function statusClass(status) {
  if (status === "pass" || status === "passed") return "pass";
  if (status === "partial") return "partial";
  return "fail";
}

function render(report) {
  const firstCase = report.testCases?.[0] || { checks: [] };
  els.score.textContent = `${report.score}`;
  els.gate.textContent = `Gate: ${report.qualityGate.minimumScore}+`;
  els.decision.textContent = report.decision;
  els.decision.className = statusClass(report.decision);
  els.summaryLine.textContent = `${firstCase.title || "Eval report"} scored from ${report.summarySource}.`;
  els.totalChecks.textContent = report.totals.totalChecks;
  els.passed.textContent = report.totals.passed;
  els.partial.textContent = report.totals.partial;
  els.failed.textContent = report.totals.failed;
  els.criticalFailures.textContent = report.totals.criticalFailures;
  els.caseTitle.textContent = firstCase.title || "No test case found.";

  clear(els.checks);
  firstCase.checks.forEach((check) => {
    const row = document.createElement("tr");
    addText(row, "td", check.title);
    addText(row, "td", check.status, statusClass(check.status));
    addText(row, "td", `${check.points} / ${check.maxPoints}`);
    addText(row, "td", check.recommendation);
    els.checks.appendChild(row);
  });

  clear(els.nextActions);
  report.nextActions.forEach((action) => addText(els.nextActions, "li", action));
}

async function loadSample() {
  const response = await fetch(sampleReportPath);
  if (!response.ok) throw new Error("Sample eval report could not be loaded.");
  render(await response.json());
}

els.upload.addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  render(JSON.parse(await file.text()));
});

loadSample().catch((error) => {
  els.decision.textContent = "Report load failed";
  els.summaryLine.textContent = error.message;
});