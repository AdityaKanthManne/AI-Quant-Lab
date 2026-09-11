"""FastAPI extension point; installed with the `api` extra."""


def create_app():
    from fastapi import FastAPI

    app = FastAPI(title="Market Simulator API", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app

