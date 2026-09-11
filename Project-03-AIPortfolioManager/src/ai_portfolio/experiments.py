from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager


@contextmanager
def tracked_run(
    run_name: str,
    parameters: Mapping[str, object],
    metrics: Mapping[str, float] | None = None,
) -> Iterator[None]:
    """Lazy MLflow integration keeps library imports usable without a tracking server."""

    import mlflow

    with mlflow.start_run(run_name=run_name):
        mlflow.log_params(dict(parameters))
        yield
        if metrics:
            mlflow.log_metrics(dict(metrics))
