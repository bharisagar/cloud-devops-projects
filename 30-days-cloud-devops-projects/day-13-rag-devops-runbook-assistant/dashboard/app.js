const sampleReportPath = "../reports/sample-rag-response.json";

const els = {
  upload: document.querySelector("#reportUpload"),
  decision: document.querySelector("#decision"),
  confidence: document.querySelector("#confidence"),
  incidentTitle: document.querySelector("#incidentTitle"),
  answerSummary: document.querySelector("#answerSummary"),
  topScore: document.querySelector("#topScore"),
  retrievedCount: document.querySelector("#retrievedCount"),
  runbookCount: document.querySelector("#runbookCount"),
  missingCount: document.querySelector("#missingCount"),
  citations: document.querySelector("#citations"),
  runbooks: document.querySelector("#runbooks"),
  checks: document.querySelector("#checks"),
  mitigation: document.querySelector("#mitigation"),
  verification: document.querySelector("#verification"),
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

function decisionClass(decision) {
  return decision === "answer_ready" ? "ready" : "review";
}

function renderList(node, items, formatter) {
  clear(node);
  items.forEach((item) => addText(node, "li", formatter(item)));
}

function render(report) {
  els.decision.textContent = report.decision;
  els.decision.className = decisionClass(report.decision);
  els.confidence.textContent = `Confidence: ${report.confidence}`;
  els.incidentTitle.textContent = report.incident.title;
  els.answerSummary.textContent = report.answer.summary;
  els.topScore.textContent = report.topScore;
  els.retrievedCount.textContent = report.retrievedChunks.length;
  els.runbookCount.textContent = report.answer.recommendedRunbooks.length;
  els.missingCount.textContent = report.missingContext.length;

  clear(els.citations);
  report.retrievedChunks.forEach((chunk) => {
    const card = document.createElement("article");
    card.className = "citation";
    addText(card, "strong", `${chunk.source} - ${chunk.heading}`);
    addText(card, "span", `Score ${chunk.score}`);
    addText(card, "p", chunk.excerpt);
    addText(card, "small", `Matched: ${chunk.matchedPhrases.join(", ") || chunk.matchedTerms.slice(0, 6).join(", ")}`);
    els.citations.appendChild(card);
  });

  renderList(els.runbooks, report.answer.recommendedRunbooks, (item) => `${item.title} (${item.source}), score ${item.score}`);
  renderList(els.checks, report.answer.immediateChecks, (item) => `${item.text} [${item.citation}]`);
  renderList(els.mitigation, report.answer.mitigationPlan, (item) => `${item.text} [${item.citation}]`);
  renderList(els.verification, report.answer.verificationSteps, (item) => `${item.text} [${item.citation}]`);
}

async function loadSample() {
  const response = await fetch(sampleReportPath);
  if (!response.ok) throw new Error("Sample RAG report could not be loaded.");
  render(await response.json());
}

els.upload.addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  render(JSON.parse(await file.text()));
});

loadSample().catch((error) => {
  els.decision.textContent = "Report load failed";
  els.answerSummary.textContent = error.message;
});