import pytest
from pydantic import ValidationError

from fin_research.models.domain import Claim, ClaimKind, ResearchRequest


def test_ticker_is_normalized() -> None:
    assert ResearchRequest(ticker=" amd ").ticker == "AMD"


def test_invalid_ticker_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ResearchRequest(ticker="not a ticker!")


def test_fact_requires_citation() -> None:
    with pytest.raises(ValidationError):
        Claim(text="Revenue rose 10%.", kind=ClaimKind.FACT)
