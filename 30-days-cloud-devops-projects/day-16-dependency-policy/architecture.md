# Architecture

```text
Invented inventory.json ------+
                               +--> check.evaluate() --> decision + findings
Versioned policy.json ---------+          |                    |
                                          |                    +--> JSON / Markdown report
                                          +--> serve.py API --> local dashboard
                                          +--> check.py CLI --> CI release gate
```

The policy engine is shared by the CLI and local-only HTTP API. It validates input
before checking every component for blocked licenses, overdue policy review, and
missing owner. Every finding has a code and a recommended action. A single finding
blocks the sample release. GitHub Actions verifies both expected outcomes and
uploads the generated report.

The invented inventory is not an SBOM and the project makes no live package,
vulnerability, or license-advisory lookups. A real pipeline would obtain
dependencies from a maintained SBOM generator, establish an exception process,
and use separate advisory data for known vulnerabilities.
