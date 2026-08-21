from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from prediction_market_agents.domain import ForecastResult, Resolution


class Base(DeclarativeBase):
    pass


class ForecastRecord(Base):
    __tablename__ = "forecasts"
    forecast_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(36), index=True)
    question: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    market_probability: Mapped[float | None] = mapped_column(Float)
    model_probability: Mapped[float] = mapped_column(Float)
    interval_low: Mapped[float] = mapped_column(Float)
    interval_high: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(100), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class ResolutionRecord(Base):
    __tablename__ = "resolutions"
    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    outcome: Mapped[int] = mapped_column(Integer)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)


class ForecastRepository:
    def __init__(self, database_url: str) -> None:
        if database_url.startswith("sqlite"):
            database = make_url(database_url).database
            if database and database != ":memory:":
                Path(database).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(database_url)

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    def save_forecast(self, forecast: ForecastResult) -> None:
        record = ForecastRecord(
            forecast_id=str(forecast.forecast_id),
            event_id=str(forecast.event_id),
            question=forecast.question,
            created_at=forecast.created_at,
            market_probability=forecast.market_probability,
            model_probability=forecast.model_probability,
            interval_low=forecast.interval_low,
            interval_high=forecast.interval_high,
            model_version=forecast.model_version,
            payload=forecast.model_dump(mode="json"),
        )
        with Session(self.engine) as session:
            session.add(record)
            session.commit()

    def resolve(self, resolution: Resolution) -> None:
        with Session(self.engine) as session:
            session.merge(
                ResolutionRecord(
                    event_id=str(resolution.event_id),
                    outcome=resolution.outcome,
                    resolved_at=resolution.resolved_at,
                    source_url=resolution.source_url,
                    notes=resolution.notes,
                )
            )
            session.commit()

    def get_forecast(self, forecast_id: UUID) -> ForecastResult | None:
        with Session(self.engine) as session:
            row = session.get(ForecastRecord, str(forecast_id))
            return None if row is None else ForecastResult.model_validate(row.payload)

    def scored_rows(self) -> list[dict[str, Any]]:
        with Session(self.engine) as session:
            rows = session.execute(
                select(ForecastRecord, ResolutionRecord).join(
                    ResolutionRecord, ForecastRecord.event_id == ResolutionRecord.event_id
                )
            ).all()
        return [
            {
                "forecast_id": f.forecast_id,
                "event_id": f.event_id,
                "created_at": f.created_at,
                "model_probability": f.model_probability,
                "market_probability": f.market_probability,
                "model_version": f.model_version,
                "outcome": r.outcome,
            }
            for f, r in rows
        ]

    def history(self, event_id: UUID) -> list[ForecastResult]:
        with Session(self.engine) as session:
            rows = session.scalars(
                select(ForecastRecord)
                .where(ForecastRecord.event_id == str(event_id))
                .order_by(ForecastRecord.created_at)
            ).all()
        return [ForecastResult.model_validate(row.payload) for row in rows]
