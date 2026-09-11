# Example notebook

The notebook phase follows the live-adapter implementation. Until then, run the same
teaching workflow without notebook metadata noise:

```python
from fin_research.models.domain import ResearchRequest
from fin_research.services import ResearchService

report = await ResearchService("demo").research(ResearchRequest(ticker="AMD"))
report.model_dump()
```

