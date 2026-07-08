import argparse
import datetime as dt
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have", "if", "in",
    "into", "is", "it", "its", "of", "on", "or", "that", "the", "this", "to", "use", "when", "with",
    "what", "which", "should", "we", "do", "few", "some", "there", "not", "yet", "after", "before",
}

IMPORTANT_PHRASE_WEIGHTS = {
    "connection pool": 18,
    "pool exhausted": 16,
    "postgres": 8,
    "database": 5,
    "checkout": 3,
    "p95 latency": 5,
    "503": 4,
    "failed traces": 5,
    "order creation": 5,
    "rollback": 6,
    "release": 4,
    "slo": 4,
    "burn rate": 6,
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(as_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(f"{key} {as_text(item)}" for key, item in value.items())
    return str(value)


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "section"


def tokenize(text):
    tokens = re.findall(r"[a-z0-9][a-z0-9_-]*", text.lower())
    return [token for token in tokens if len(token) > 1 and token not in STOPWORDS]


def parse_markdown(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    title = Path(path).stem.replace("-", " ").title()
    chunks = []
    heading = "Overview"
    body = []

    def flush():
        text = "\n".join(body).strip()
        if text:
            chunk_id = f"{Path(path).name}#{slugify(heading)}"
            chunks.append(
                {
                    "id": chunk_id,
                    "source": Path(path).name,
                    "title": title,
                    "heading": heading,
                    "text": text,
                }
            )

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            flush()
            heading = line[3:].strip()
            body = []
            continue
        body.append(line)

    flush()
    return chunks


def load_chunks(knowledge_base):
    chunks = []
    for path in sorted(Path(knowledge_base).glob("*.md")):
        chunks.extend(parse_markdown(path))
    return chunks


def build_query_text(incident):
    return as_text(
        [
            incident.get("title"),
            incident.get("severity"),
            incident.get("services"),
            incident.get("summary"),
            incident.get("symptoms"),
            incident.get("signals"),
            incident.get("recentChanges"),
            incident.get("question"),
        ]
    )


def score_chunk(query_text, query_terms, chunk):
    chunk_text = as_text([chunk["source"], chunk["title"], chunk["heading"], chunk["text"]])
    chunk_terms = Counter(tokenize(chunk_text))
    overlap = set(query_terms) & set(chunk_terms)
    raw_score = sum(query_terms[token] * chunk_terms[token] for token in overlap)

    query_lower = query_text.lower()
    chunk_lower = chunk_text.lower()
    phrase_bonus = 0
    matched_phrases = []
    for phrase, weight in IMPORTANT_PHRASE_WEIGHTS.items():
        if phrase in query_lower and phrase in chunk_lower:
            phrase_bonus += weight
            matched_phrases.append(phrase)

    length_norm = math.sqrt(max(1, len(chunk_terms)))
    score = round((raw_score + phrase_bonus) / length_norm * 10, 2)
    return score, sorted(overlap), matched_phrases


def rank_chunks(incident, chunks):
    query_text = build_query_text(incident)
    query_terms = Counter(tokenize(query_text))
    ranked = []
    for chunk in chunks:
        score, overlap, matched_phrases = score_chunk(query_text, query_terms, chunk)
        if score > 0:
            ranked.append(
                {
                    **chunk,
                    "score": score,
                    "matchedTerms": overlap[:18],
                    "matchedPhrases": matched_phrases,
                    "excerpt": chunk["text"].replace("\n", " ")[:260],
                }
            )
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked, query_terms


def source_rank(ranked_chunks):
    scores = defaultdict(float)
    titles = {}
    for chunk in ranked_chunks:
        scores[chunk["source"]] = max(scores[chunk["source"]], chunk["score"])
        titles[chunk["source"]] = chunk["title"]
    return [
        {"source": source, "title": titles[source], "score": round(score, 2)}
        for source, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)
    ]


def bullets_from_chunk(chunk):
    bullets = []
    for line in chunk["text"].splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def collect_bullets(chunks, source_order, headings, limit):
    results = []
    seen = set()
    source_rank = {source: index for index, source in enumerate(source_order)}
    ordered_chunks = sorted(chunks, key=lambda chunk: (source_rank.get(chunk["source"], 999), chunk["heading"]))
    for chunk in ordered_chunks:
        if chunk["source"] not in source_rank:
            continue
        if chunk["heading"] not in headings:
            continue
        for bullet in bullets_from_chunk(chunk):
            key = bullet.lower()
            if key in seen:
                continue
            seen.add(key)
            results.append({"text": bullet, "citation": chunk["id"]})
            if len(results) >= limit:
                return results
    return results


def detect_missing_context(incident):
    missing = []
    if not incident.get("services"):
        missing.append("service names")
    signals = incident.get("signals") or {}
    if "peakErrorRatePercent" not in signals:
        missing.append("error rate")
    if "peakP95LatencyMs" not in signals:
        missing.append("p95 latency")
    if not incident.get("recentChanges"):
        missing.append("recent deployment or configuration changes")
    if len(incident.get("symptoms") or []) < 3:
        missing.append("specific symptoms from logs, metrics, or traces")
    return missing


def confidence_for(ranked_chunks, incident):
    if not ranked_chunks:
        return "low", 0, []

    top_score = ranked_chunks[0]["score"]
    source_count = len({chunk["source"] for chunk in ranked_chunks[:6]})
    missing = detect_missing_context(incident)

    if top_score >= 18 and source_count >= 2 and len(missing) <= 1:
        return "high", top_score, missing
    if top_score >= 8 and len(missing) <= 2:
        return "medium", top_score, missing
    return "low", top_score, missing


def build_answer(incident, all_chunks, ranked_chunks):
    top_sources = source_rank(ranked_chunks)[:3]
    source_order = [source["source"] for source in top_sources]
    source_titles = [source["title"] for source in top_sources]

    immediate_checks = collect_bullets(all_chunks, source_order, {"Immediate Checks"}, 7)
    mitigation = collect_bullets(all_chunks, source_order, {"Mitigation", "Rollback Criteria"}, 7)
    verification = collect_bullets(all_chunks, source_order, {"Verification"}, 6)

    if not immediate_checks:
        immediate_checks = [{"text": "Collect service name, error rate, latency, logs, traces, and recent changes before acting.", "citation": "human-review"}]
    if not mitigation:
        mitigation = [{"text": "Avoid automated mitigation until the incident has stronger evidence and an owner confirms impact.", "citation": "human-review"}]
    if not verification:
        verification = [{"text": "Define recovery metrics before declaring the incident resolved.", "citation": "human-review"}]

    best = top_sources[0] if top_sources else {"title": "No strong runbook match", "source": "none"}
    return {
        "summary": (
            f"The best matching runbook is {best['title']} for incident {incident.get('id', 'unknown')}. "
            "Use the retrieved citations as responder guidance, not as fully automated remediation."
        ),
        "recommendedRunbooks": top_sources,
        "immediateChecks": immediate_checks,
        "mitigationPlan": mitigation,
        "verificationSteps": verification,
        "escalationNote": (
            "Escalate to the service owner and incident lead if customer impact continues, if rollback risk is unclear, "
            "or if the retrieved runbooks do not explain the observed telemetry."
        ),
        "sourceCoverage": source_titles,
    }


def build_report(incident, knowledge_base, top_k):
    chunks = load_chunks(knowledge_base)
    ranked, query_terms = rank_chunks(incident, chunks)
    retrieved = ranked[:top_k]
    confidence, top_score, missing_context = confidence_for(retrieved, incident)
    decision = "answer_ready" if confidence in {"high", "medium"} else "needs_human_review"
    answer = build_answer(incident, chunks, retrieved)

    return {
        "project": "Day 13 - Local RAG DevOps Runbook Assistant",
        "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
        "incident": {
            "id": incident.get("id"),
            "title": incident.get("title"),
            "severity": incident.get("severity"),
            "services": incident.get("services", []),
            "question": incident.get("question"),
        },
        "knowledgeBase": str(knowledge_base),
        "decision": decision,
        "confidence": confidence,
        "topScore": top_score,
        "missingContext": missing_context,
        "queryTerms": [term for term, _count in query_terms.most_common(25)],
        "retrievedChunks": retrieved,
        "answer": answer,
    }


def markdown_cell(value):
    return as_text(value).replace("\n", " ").replace("|", "\\|")


def write_markdown(report, output_path):
    lines = [
        "# Local RAG Runbook Assistant Report",
        "",
        f"Generated: {report['generatedAt']}",
        "",
        f"Decision: {report['decision']}",
        "",
        f"Confidence: {report['confidence']}",
        "",
        f"Incident: {report['incident']['title']}",
        "",
        "## Answer",
        "",
        report["answer"]["summary"],
        "",
        "## Recommended Runbooks",
        "",
    ]

    for runbook in report["answer"]["recommendedRunbooks"]:
        lines.append(f"- {runbook['title']} (`{runbook['source']}`), score {runbook['score']}")

    lines.extend(["", "## Immediate Checks", ""])
    for item in report["answer"]["immediateChecks"]:
        lines.append(f"- {item['text']} [{item['citation']}]")

    lines.extend(["", "## Mitigation Plan", ""])
    for item in report["answer"]["mitigationPlan"]:
        lines.append(f"- {item['text']} [{item['citation']}]")

    lines.extend(["", "## Verification Steps", ""])
    for item in report["answer"]["verificationSteps"]:
        lines.append(f"- {item['text']} [{item['citation']}]")

    lines.extend(["", "## Retrieved Chunks", "", "| Source | Heading | Score | Matched Phrases |", "| --- | --- | ---: | --- |"])
    for chunk in report["retrievedChunks"]:
        lines.append(
            f"| {markdown_cell(chunk['source'])} | {markdown_cell(chunk['heading'])} | {chunk['score']} | {markdown_cell(', '.join(chunk['matchedPhrases']))} |"
        )

    if report["missingContext"]:
        lines.extend(["", "## Missing Context", ""])
        for item in report["missingContext"]:
            lines.append(f"- {item}")

    lines.extend(["", "## Escalation Note", "", report["answer"]["escalationNote"], ""])
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Retrieve local DevOps runbooks and build a cited incident response.")
    parser.add_argument("--incident", default="incidents/sample-checkout-incident.json")
    parser.add_argument("--knowledge-base", default="knowledge-base/runbooks")
    parser.add_argument("--top-k", type=int, default=6)
    parser.add_argument("--output-json", default="reports/sample-rag-response.json")
    parser.add_argument("--output-md", default="reports/sample-rag-response.md")
    parser.add_argument("--enforce-confidence", action="store_true", help="Exit non-zero when the response needs human review.")
    args = parser.parse_args()

    incident = load_json(args.incident)
    report = build_report(incident, Path(args.knowledge_base), args.top_k)

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, output_md)

    top_source = report["retrievedChunks"][0]["source"] if report["retrievedChunks"] else "none"
    print(f"Decision: {report['decision']}")
    print(f"Confidence: {report['confidence']}")
    print(f"Top source: {top_source}")
    print(f"JSON report: {output_json}")
    print(f"Markdown report: {output_md}")

    if args.enforce_confidence and report["decision"] != "answer_ready":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())