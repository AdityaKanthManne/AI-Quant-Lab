# Architecture decisions

## Scientific control plane

LangGraph models the research lifecycle as explicit state transitions. Each role accepts and returns
typed research state. The code-execution edge is conditional: an unapproved artifact skips execution
and goes directly to review. This makes autonomy observable and interruptible.

## Research memory

The canonical artifact hierarchy is human-readable and append-oriented. PostgreSQL stores normalized
metadata and graph-like edges; Qdrant indexes chunks and structured extractions for semantic retrieval;
DuckDB and Polars handle local analytical data; MLflow indexes run parameters and metrics. Files remain
the reproducibility boundary so a project can be archived without a running service.

## Knowledge graph in PostgreSQL

Use typed nodes (`paper`, `model`, `dataset`, `question`, `result`) and typed edges (`uses`,
`evaluates`, `investigates`, `cites`, `reports`). Start with relational tables and indexed foreign keys;
add recursive CTEs for traversal. A dedicated graph database is unnecessary until traversal complexity
or scale is measured.

## Trust boundaries

Literature claims require DOI, arXiv, or Semantic Scholar identifiers. Extracted fields retain evidence
spans. Generated code is stored before review, requires explicit approval, and runs in Docker without a
network, Linux capabilities, or write access outside its run directory. Production deployments should
also use a separate worker host and allowlisted base images.

