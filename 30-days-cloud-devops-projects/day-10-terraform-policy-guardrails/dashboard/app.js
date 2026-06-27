const sampleReportPath = "../reports/sample-policy-report.json";

const els = {
  riskScore: document.querySelector("#riskScore"),
  decisionText: document.querySelector("#decisionText"),
  decision: document.querySelector("#decision"),
  minimumScore: document.querySelector("#minimumScore"),
  blockOnCritical: document.querySelector("#blockOnCritical"),
  totalFindings: document.querySelector("#totalFindings"),
  criticalFindings: document.querySelector("#criticalFindings"),
  highFindings: document.querySelector("#highFindings"),
  mediumFindings: document.querySelector("#mediumFindings"),
  lowFindings: document.querySelector("#lowFindings"),
  findings: document.querySelector("#findings"),
  upload: document.querySelector("#reportUpload"),
};

function severityClass(severity) {
  return `severity-${String(severity).toLowerCase()}`;
}

function decisionMessage(report) {
  if (report.decision === "approved") {
    return "Plan passed the deployment gate.";
  }
  if ((report.summary?.critical ?? 0) > 0) {
    return "Blocked because critical policy findings exist.";
  }
  return "Blocked because the risk score is below the minimum gate.";
}

function setText(key, value) {
  els[key].textContent = value ?? "--";
}

function renderSummary(report) {
  setText("riskScore", `${report.riskScore ?? 0}/100`);
  setText("decisionText", decisionMessage(report));
  setText("decision", report.decision || "unknown");
  els.decision.className = report.decision === "approved" ? "decision-approved" : "decision-blocked";
  setText("minimumScore", report.deploymentGate?.minimumScore ?? "--");
  setText("blockOnCritical", report.deploymentGate?.blockOnCritical ? "Yes" : "No");
  setText("totalFindings", report.summary?.totalFindings ?? report.findings?.length ?? 0);
  setText("criticalFindings", report.summary?.critical ?? 0);
  setText("highFindings", report.summary?.high ?? 0);
  setText("mediumFindings", report.summary?.medium ?? 0);
  setText("lowFindings", report.summary?.low ?? 0);
}

function renderFindings(findings = []) {
  if (!findings.length) {
    els.findings.innerHTML = `<div class="finding"><h4>No findings detected</h4><p>The Terraform plan passed all configured guardrails.</p></div>`;
    return;
  }

  els.findings.innerHTML = findings
    .map(
      (finding) => `
        <article class="finding">
          <div class="finding-top">
            <h4>${finding.title}</h4>
            <span class="badge ${severityClass(finding.severity)}">${finding.severity}</span>
          </div>
          <p><strong>Resource:</strong> ${finding.resource}</p>
          <p><strong>Detail:</strong> ${finding.detail}</p>
          <p><strong>Fix:</strong> ${finding.recommendation}</p>
        </article>
      `
    )
    .join("");
}

function render(report) {
  renderSummary(report);
  renderFindings(report.findings || []);
}

async function loadSample() {
  const response = await fetch(sampleReportPath);
  if (!response.ok) throw new Error("Sample report could not be loaded.");
  render(await response.json());
}

els.upload.addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  const text = await file.text();
  render(JSON.parse(text));
});

loadSample().catch((error) => {
  els.findings.innerHTML = `<div class="finding"><h4>Report load failed</h4><p>${error.message}</p></div>`;
});
