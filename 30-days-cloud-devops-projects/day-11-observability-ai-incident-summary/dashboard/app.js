const sampleReportPath = "../reports/sample-incident-summary.json";

const els = {
  upload: document.querySelector("#reportUpload"),
  title: document.querySelector("#title"),
  summary: document.querySelector("#summary"),
  severity: document.querySelector("#severity"),
  status: document.querySelector("#status"),
  sloStatus: document.querySelector("#sloStatus"),
  logEvents: document.querySelector("#logEvents"),
  metricPoints: document.querySelector("#metricPoints"),
  traceCount: document.querySelector("#traceCount"),
  failedTraceCount: document.querySelector("#failedTraceCount"),
  peakErrorRate: document.querySelector("#peakErrorRate"),
  rootCause: document.querySelector("#rootCause"),
  evidence: document.querySelector("#evidence"),
  timeline: document.querySelector("#timeline"),
  commands: document.querySelector("#commands"),
  remediation: document.querySelector("#remediation"),
  verification: document.querySelector("#verification"),
};

function list(items = []) {
  return items.map((item) => `<li>${item}</li>`).join("");
}

function render(report) {
  els.title.textContent = report.title;
  els.summary.textContent = report.summary;
  els.severity.textContent = report.severity;
  els.status.textContent = report.status;
  els.sloStatus.textContent = report.slo.status;
  els.logEvents.textContent = report.signals.logEvents;
  els.metricPoints.textContent = report.signals.metricPoints;
  els.traceCount.textContent = report.signals.traceCount;
  els.failedTraceCount.textContent = report.signals.failedTraceCount;
  els.peakErrorRate.textContent = `${report.slo.peakErrorRatePercent}%`;
  els.rootCause.textContent = report.probableRootCause;
  els.evidence.innerHTML = list(report.evidence);
  els.timeline.innerHTML = report.timeline
    .map((event) => `<div class="event"><strong>${event.timestamp} - ${event.service}</strong><span>${event.message}</span></div>`)
    .join("");
  els.commands.innerHTML = report.recommendedCommands
    .map((command) => `<div class="command">$ ${command}</div>`)
    .join("");
  els.remediation.innerHTML = list(report.remediationPlan);
  els.verification.innerHTML = list(report.verificationChecklist);
}

async function loadSample() {
  const response = await fetch(sampleReportPath);
  if (!response.ok) throw new Error("Sample incident summary could not be loaded.");
  render(await response.json());
}

els.upload.addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  render(JSON.parse(await file.text()));
});

loadSample().catch((error) => {
  els.title.textContent = "Report load failed";
  els.summary.textContent = error.message;
});