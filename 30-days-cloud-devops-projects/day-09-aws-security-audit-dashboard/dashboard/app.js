const sampleReportPath = "../reports/sample-audit-report.json";

const els = {
  riskScore: document.querySelector("#riskScore"),
  riskLabel: document.querySelector("#riskLabel"),
  accountId: document.querySelector("#accountId"),
  region: document.querySelector("#region"),
  generatedAt: document.querySelector("#generatedAt"),
  totalFindings: document.querySelector("#totalFindings"),
  criticalFindings: document.querySelector("#criticalFindings"),
  highFindings: document.querySelector("#highFindings"),
  mediumFindings: document.querySelector("#mediumFindings"),
  lowFindings: document.querySelector("#lowFindings"),
  findings: document.querySelector("#findings"),
  serviceChecks: document.querySelector("#serviceChecks"),
  iamUsers: document.querySelector("#iamUsers"),
  upload: document.querySelector("#reportUpload"),
};

function riskLabel(score) {
  if (score >= 85) return "Strong security posture";
  if (score >= 70) return "Good, with a few improvements";
  if (score >= 50) return "Needs security hardening";
  return "High-risk posture. Fix priority findings first.";
}

function severityClass(severity) {
  return `severity-${String(severity).toLowerCase()}`;
}

function setText(key, value) {
  els[key].textContent = value ?? "--";
}

function renderSummary(report) {
  const score = report.riskScore ?? 0;
  setText("riskScore", `${score}/100`);
  setText("riskLabel", riskLabel(score));
  setText("accountId", report.identity?.Account || "unknown");
  setText("region", report.region || "unknown");
  setText("generatedAt", report.generatedAt ? new Date(report.generatedAt).toLocaleString() : "unknown");
  setText("totalFindings", report.summary?.totalFindings ?? report.findings?.length ?? 0);
  setText("criticalFindings", report.summary?.critical ?? 0);
  setText("highFindings", report.summary?.high ?? 0);
  setText("mediumFindings", report.summary?.medium ?? 0);
  setText("lowFindings", report.summary?.low ?? 0);
}

function renderFindings(findings = []) {
  if (!findings.length) {
    els.findings.innerHTML = `<div class="finding"><h4>No findings detected</h4><p>The collector did not detect risky signals in this report.</p></div>`;
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
          <p><strong>Fix:</strong> ${finding.recommendation}</p>
        </article>
      `
    )
    .join("");
}

function checkStatus(label, value, badWhenZero = false) {
  const isBad = badWhenZero ? value === 0 : value > 0;
  return `
    <div class="check-row">
      <div>
        <strong>${label}</strong>
        <p>${value}</p>
      </div>
      <span class="status ${isBad ? "bad" : ""}"></span>
    </div>
  `;
}

function renderServiceChecks(checks = {}) {
  const usersWithoutMfa = (checks.users || []).filter((user) => user.hasMfa === false).length;
  const oldKeys = (checks.users || []).flatMap((user) => user.accessKeys || []).filter((key) => key.ageDays > 90).length;
  const publicBuckets = (checks.s3Buckets || []).filter((bucket) => bucket.hasPublicAclGrant || bucket.hasPublicAccessBlock === false).length;
  const openSecurityGroups = (checks.openSecurityGroups || []).length;
  const loggingTrails = (checks.cloudTrail || []).filter((trail) => trail.isLogging === true).length;
  const budgets = checks.budgetCount ?? 0;

  els.serviceChecks.innerHTML = [
    checkStatus("Users without MFA", usersWithoutMfa),
    checkStatus("Access keys older than 90 days", oldKeys),
    checkStatus("S3 public risk signals", publicBuckets),
    checkStatus("Open security group rules", openSecurityGroups),
    checkStatus("Active CloudTrail trails", loggingTrails, true),
    checkStatus("AWS Budgets configured", budgets, true),
  ].join("");
}

function renderIamUsers(users = []) {
  if (!users.length) {
    els.iamUsers.innerHTML = `<tr><td colspan="4">No IAM users found in this report.</td></tr>`;
    return;
  }

  els.iamUsers.innerHTML = users
    .map((user) => {
      const keys = (user.accessKeys || []).map((key) => `${key.status} - ${key.ageDays} days`).join("<br>") || "No access keys";
      const policies = (user.attachedPolicies || []).join("<br>") || "No direct policies";
      return `
        <tr>
          <td>${user.userName}</td>
          <td>${user.hasMfa ? "Enabled" : "Missing"}</td>
          <td>${policies}</td>
          <td>${keys}</td>
        </tr>
      `;
    })
    .join("");
}

function render(report) {
  renderSummary(report);
  renderFindings(report.findings || []);
  renderServiceChecks(report.checks || {});
  renderIamUsers(report.checks?.users || []);
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
