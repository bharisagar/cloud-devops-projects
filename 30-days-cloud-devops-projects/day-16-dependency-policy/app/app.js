const $ = (id) => document.getElementById(id);
let currentReport = null;
let selected = "risky";

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[character]));
}

async function loadSample(kind) {
  selected = kind;
  $("risky").classList.toggle("active", kind === "risky");
  $("clean").classList.toggle("active", kind === "clean");
  const response = await fetch(kind === "risky" ? "/api/sample" : "/api/clean");
  if (!response.ok) throw new Error("Could not load sample inventory.");
  const sample = await response.json();
  $("inventory-json").value = JSON.stringify(sample.inventory, null, 2);
  $("policy-json").value = JSON.stringify(sample.policy, null, 2);
  await evaluate();
}

async function evaluate() {
  $("error").hidden = true;
  try {
    const inventory = JSON.parse($("inventory-json").value);
    const policy = JSON.parse($("policy-json").value);
    const response = await fetch("/api/evaluate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({inventory, policy})
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Evaluation failed.");
    currentReport = result;
    render(result);
  } catch (error) {
    currentReport = null;
    $("download").disabled = true;
    $("error").textContent = error.message;
    $("error").hidden = false;
  }
}

function render(report) {
  const blocked = report.decision === "BLOCK";
  $("as-of").textContent = report.as_of;
  $("decision").textContent = report.decision;
  $("decision-icon").textContent = blocked ? "!" : "✓";
  $("decision-note").textContent = blocked ? "Release held until every policy finding is resolved." : "All components meet the current policy.";
  document.querySelector(".decision-row").classList.toggle("pass", !blocked);
  $("count-components").textContent = report.summary.components;
  $("count-blocked").textContent = report.summary.blocked_components;
  $("count-findings").textContent = report.summary.findings;
  $("inventory-count").textContent = report.summary.components + " COMPONENTS";
  $("finding-count").textContent = report.summary.findings + " FINDINGS";
  $("download").disabled = false;
  $("component-rows").innerHTML = report.components.map((item) => `<tr>
    <td class="component-name">${escapeHtml(item.name)}</td>
    <td class="mono">${escapeHtml(item.version)}</td>
    <td class="mono">${escapeHtml(item.license)}</td>
    <td>${escapeHtml(item.owner || "Unassigned")}</td>
    <td class="mono">${escapeHtml(item.last_reviewed)}</td>
    <td><span class="status ${item.status === "BLOCK" ? "status-block" : "status-pass"}">${escapeHtml(item.status)}</span></td>
  </tr>`).join("");
  $("finding-list").innerHTML = report.findings.length ? report.findings.map((item, index) => `<article class="finding">
    <span class="finding-index">${String(index + 1).padStart(2, "0")}</span>
    <div><div class="finding-top"><strong>${escapeHtml(item.component)}</strong><span class="finding-code">${escapeHtml(item.code.replaceAll("_", " "))}</span></div>
    <p>${escapeHtml(item.detail)}</p><small>${escapeHtml(item.action)}</small></div>
  </article>`).join("") : '<div class="empty">No findings. This inventory meets the selected policy.</div>';
}

$("risky").addEventListener("click", () => loadSample("risky").catch(showLoadError));
$("clean").addEventListener("click", () => loadSample("clean").catch(showLoadError));
$("evaluate").addEventListener("click", evaluate);
$("download").addEventListener("click", () => {
  if (!currentReport) return;
  const blob = new Blob([JSON.stringify(currentReport, null, 2) + "\n"], {type: "application/json"});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "day-16-policy-report.json";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
function showLoadError(error) {
  $("error").textContent = error.message;
  $("error").hidden = false;
}
loadSample(selected).catch(showLoadError);
