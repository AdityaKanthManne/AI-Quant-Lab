from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class SecClient:
    user_agent: str
    timeout_seconds: float = 20.0

    async def company_submissions(self, cik: str) -> dict:
        normalized = cik.zfill(10)
        headers = {"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"}
        async with httpx.AsyncClient(headers=headers, timeout=self.timeout_seconds) as client:
            response = await client.get(f"https://data.sec.gov/submissions/CIK{normalized}.json")
            response.raise_for_status()
            return response.json()

