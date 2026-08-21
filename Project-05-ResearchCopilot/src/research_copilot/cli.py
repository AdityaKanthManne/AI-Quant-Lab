import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous Quantitative Research Copilot")
    parser.add_argument("command", choices=["serve"])
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.command == "serve":
        uvicorn.run("research_copilot.api:app", host="0.0.0.0", port=args.port, reload=False)

