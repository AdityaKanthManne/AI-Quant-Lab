# Architecture Notes

The system uses an evidence-first pipeline. Source adapters retrieve facts and preserve
provenance. Specialist agents transform source records into typed `AgentResult` objects.
The supervisor synthesizes only those objects, and the output guard validates citations
before the API boundary.

## Production implementation sequence

1. Implement SEC ticker-to-CIK resolution, submissions retrieval, filing parsing, and XBRL facts.
2. Implement market/fundamental retrieval with caching and explicit field provenance.
3. Implement FRED series selection and observation-date handling.
4. Add GDELT and investor-relations ingestion with deduplication.
5. Chunk filing sections and index them in Qdrant.
6. Persist run metadata and reports in PostgreSQL.
7. Add a grounded structured-output LLM behind the supervisor interface.
8. Add temporal backtests and human relevance labels to evaluation.

Never quietly substitute demo fixtures for unavailable live data.

