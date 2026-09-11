# Base code outline

## Package map

```text
src/research_copilot/
├── api.py          # FastAPI transport layer
├── agents.py       # ten-role LangGraph lifecycle and approval branch
├── models.py       # validated research-domain contracts
├── ports.py        # interfaces for infrastructure adapters
├── literature.py   # arXiv and Crossref clients
├── storage.py      # append-oriented local research memory
├── runner.py       # reviewed, isolated experiment execution
├── statistics.py   # statistical estimation and corrections
├── evaluation.py   # citation and claim-grounding checks
├── reporting.py    # report structure and claim separation
├── config.py       # environment-backed settings
└── cli.py          # command-line entry point
```

## Agent contracts

Each agent receives `ResearchState` and returns only the fields it owns:

| Agent | Reads | Produces |
|---|---|---|
| Literature Search | question | verified paper metadata |
| Paper Extraction | papers/full text | structured extractions plus evidence spans |
| Research Gap | extractions | contradictions, omissions, open questions |
| Hypothesis | question/gaps | falsifiable hypotheses |
| Dataset Discovery | hypotheses | dataset cards and provenance |
| Experimental Design | hypothesis/datasets | `ExperimentSpec` |
| Statistical Analysis | specification | estimands, tests, uncertainty plan |
| Code Execution | approved artifact | immutable run artifacts |
| Critic/Reviewer | all evidence | severity-ranked findings |
| Report Generation | evidence/findings | sectioned report with typed claims |

## Implementation order

1. Add SQLAlchemy models and migrations for paper, dataset, experiment, node, and edge records.
2. Implement the `PaperRepository` port using PostgreSQL.
3. Chunk evidence-bearing paper text and implement `SemanticIndex` with Qdrant.
4. Add a provider-neutral structured-output language-model adapter.
5. Replace each placeholder role handler with a separately tested service.
6. Add point-in-time dataset snapshots, checksums, and licensing records.
7. Connect the runner to MLflow and require a persisted review decision.
8. Add resumable LangGraph checkpoints and API endpoints for approvals.
9. Generate HTML/PDF reports with claim-to-artifact links.
10. Add authentication and move untrusted execution onto isolated workers.

The important boundary is evidence provenance: a paper extraction points to source text, a dataset points
to a version and checksum, a numerical result points to a run, and every conclusion points to one or more
of those artifacts.

