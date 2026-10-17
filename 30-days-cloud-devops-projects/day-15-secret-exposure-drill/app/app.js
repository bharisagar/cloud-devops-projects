const byId = (id) => document.getElementById(id);
let latestReport = null;

function setStatus(message) { byId("status").textContent = message; }
function updateLineCount() {
  const text = byId("sourceText").value;
  byId("lineCount").textContent = `${text ? text.replace(/\r?\n$/, "").split(/\r?\n/).length : 0} lines`;
}

function addFinding(finding) {
  const item = document.createElement("article");
  item.className = "finding";
  const line = document.createElement("span");
  line.className = "finding-line";
  line.textContent = finding.line;
  const content = document.createElement("div");
  const title = document.createElement("div");
  title.className = "finding-title";
  const name = document.createElement("span");
  name.textContent = finding.title;
  const severity = document.createElement("em");
  severity.textContent = finding.severity;
  const action = document.createElement("p");
  action.textContent = finding.action;
  title.append(name, severity);
  content.append(title, action);
  item.append(line, content);
  return item;
}

function render(report) {
  latestReport = report;
  byId("riskScore").textContent = report.risk_score;
  byId("findingCount").textContent = report.findings.length;
  byId("scannedCount").textContent = report.lines_scanned;
  byId("decisionText").textContent = report.decision;
  byId("findingLabel").textContent = `${report.findings.length} items`;
  const state = byId("scanState");
  state.textContent = report.findings.length ? "Action required" : "No matches";
  state.className = `state-pill ${report.findings.length ? "alert" : "clear"}`;
  const findings = byId("findings");
  findings.replaceChildren();
  if (report.findings.length) {
    report.findings.forEach((finding) => findings.append(addFinding(finding)));
  } else {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "No training-rule matches were found.";
    findings.append(empty);
  }
  const steps = byId("responseSteps");
  steps.replaceChildren();
  report.response_steps.forEach((step) => {
    const item = document.createElement("li");
    item.textContent = step;
    steps.append(item);
  });
  byId("limitations").textContent = report.limitations;
  byId("downloadButton").disabled = false;
}

async function analyze() {
  const text = byId("sourceText").value;
  byId("analyzeButton").disabled = true;
  setStatus("Scanning...");
  try {
    const response = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const report = await response.json();
    if (!response.ok) throw new Error(report.error || "Scan failed");
    render(report);
    setStatus("Scan complete");
  } catch (error) {
    setStatus(error.message);
  } finally {
    byId("analyzeButton").disabled = false;
  }
}

async function loadSample() {
  setStatus("Loading sample...");
  try {
    const response = await fetch("/api/sample");
    if (!response.ok) throw new Error("Could not load sample");
    byId("sourceText").value = (await response.json()).text;
    updateLineCount();
    await analyze();
  } catch (error) {
    setStatus(error.message);
  }
}

function download() {
  if (!latestReport) return;
  const blob = new Blob([JSON.stringify(latestReport, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "day-15-secret-exposure-report.json";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

byId("sourceText").addEventListener("input", updateLineCount);
byId("analyzeButton").addEventListener("click", analyze);
byId("sampleButton").addEventListener("click", loadSample);
byId("downloadButton").addEventListener("click", download);
byId("clearButton").addEventListener("click", () => { byId("sourceText").value = ""; updateLineCount(); setStatus("Ready"); });
loadSample();
