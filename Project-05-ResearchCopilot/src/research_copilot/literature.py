from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

from research_copilot.models import PaperIdentifier, PaperMetadata


class LiteratureClient:
    """Public-source literature search with identifier-first normalization."""

    def __init__(self, timeout: float = 20):
        self.timeout = timeout

    async def search(self, query: str, sources: list[str], limit: int) -> list[PaperMetadata]:
        papers: list[PaperMetadata] = []
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            if "arxiv" in sources:
                papers.extend(await self._arxiv(client, query, limit))
            if "crossref" in sources:
                papers.extend(await self._crossref(client, query, limit))
        deduplicated: dict[str, PaperMetadata] = {}
        for paper in papers:
            key = paper.identifiers.doi or paper.identifiers.arxiv_id or str(paper.id)
            deduplicated[key.lower()] = paper
        return list(deduplicated.values())[:limit]

    async def _arxiv(self, client: httpx.AsyncClient, query: str, limit: int) -> list[PaperMetadata]:
        response = await client.get(
            "https://export.arxiv.org/api/query",
            params={"search_query": f"all:{query}", "start": 0, "max_results": limit},
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        output = []
        for entry in root.findall("atom:entry", ns):
            raw_id = entry.findtext("atom:id", default="", namespaces=ns)
            arxiv_id = raw_id.rsplit("/", 1)[-1]
            authors = [a.findtext("atom:name", default="", namespaces=ns) for a in entry.findall("atom:author", ns)]
            published = entry.findtext("atom:published", default="", namespaces=ns)
            output.append(PaperMetadata(
                title=" ".join(entry.findtext("atom:title", default="", namespaces=ns).split()),
                abstract=" ".join(entry.findtext("atom:summary", default="", namespaces=ns).split()),
                authors=authors,
                year=int(published[:4]) if published else None,
                url=raw_id,
                identifiers=PaperIdentifier(arxiv_id=arxiv_id),
                source="arxiv",
            ))
        return output

    async def _crossref(self, client: httpx.AsyncClient, query: str, limit: int) -> list[PaperMetadata]:
        response = await client.get(
            "https://api.crossref.org/works",
            params={"query": query, "rows": limit, "select": "DOI,title,author,published,URL,container-title,is-referenced-by-count,abstract"},
            headers={"User-Agent": "ResearchCopilot/0.1 (mailto:research@example.com)"},
        )
        response.raise_for_status()
        output = []
        for item in response.json()["message"]["items"]:
            if not item.get("DOI") or not item.get("title"):
                continue
            authors = [" ".join(filter(None, (a.get("given"), a.get("family")))) for a in item.get("author", [])]
            dates = item.get("published", {}).get("date-parts", [[]])
            output.append(PaperMetadata(
                title=item["title"][0], abstract=item.get("abstract"), authors=authors,
                year=dates[0][0] if dates and dates[0] else None,
                venue=(item.get("container-title") or [None])[0], url=item.get("URL"),
                identifiers=PaperIdentifier(doi=item["DOI"]),
                citation_count=item.get("is-referenced-by-count"), source="crossref",
            ))
        return output
