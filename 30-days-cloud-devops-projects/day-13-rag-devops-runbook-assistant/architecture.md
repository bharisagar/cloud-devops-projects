# Day 13 Architecture

The Day 13 project adds a retrieval layer between incident context and response planning.

## Flow

```text
Incident JSON
  -> extract query terms
  -> chunk markdown runbooks
  -> score chunks by overlap and operational keywords
  -> keep top citations
  -> build a response plan
  -> write JSON and Markdown reports
  -> render dashboard evidence
```

## Components

| Component | Purpose |
| --- | --- |
| `incidents/sample-checkout-incident.json` | Detailed incident context that should retrieve strong runbooks. |
| `incidents/vague-incident.json` | Weak incident context used to prove the assistant can ask for human review. |
| `knowledge-base/runbooks/` | Local markdown runbooks used as the retrieval corpus. |
| `scripts/runbook_assistant.py` | Lightweight RAG-style retriever and response builder. |
| `reports/sample-rag-response.json` | Machine-readable response with citations and confidence. |
| `reports/sample-rag-response.md` | Human-readable evidence report. |
| `dashboard/` | Browser dashboard for retrieved chunks, answer, and next actions. |

## Mermaid Diagram

```mermaid
flowchart TD
    A["Incident Context JSON"] --> B["Query Builder"]
    C["Markdown Runbooks"] --> D["Chunker"]
    B --> E["Retriever"]
    D --> E
    E --> F["Ranked Citations"]
    F --> G["Response Builder"]
    G --> H{"Confidence Check"}
    H -->|High or Medium| I["answer_ready"]
    H -->|Low| J["needs_human_review"]
    G --> K["JSON and Markdown Reports"]
    K --> L["Dashboard Evidence"]
```

## Why This Matters

RAG is useful in DevOps when teams have internal runbooks, past incident notes, architecture decisions, or postmortems. The key habit is grounding recommendations in retrieved sources so responders can inspect the evidence before acting.