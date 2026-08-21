from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from research_copilot.models import CodeArtifact, ReviewStatus


class ExecutionRejected(RuntimeError):
    pass


class ExperimentRunner:
    """Runs approved Python in a constrained Docker container with immutable artifacts."""

    forbidden_fragments = ("--privileged", "/var/run/docker.sock", "--network=host")

    def __init__(self, projects_root: Path, timeout_seconds: int = 300):
        self.projects_root = projects_root
        self.timeout_seconds = timeout_seconds

    def execute(self, project_slug: str, artifact: CodeArtifact) -> Path:
        if artifact.status != ReviewStatus.APPROVED:
            raise ExecutionRejected("Code must be explicitly approved before execution")
        experiment_dir = self.projects_root / project_slug / "experiments" / str(artifact.experiment_id)
        if not experiment_dir.is_dir():
            raise FileNotFoundError(experiment_dir)
        run_id = f"{datetime.now(UTC):%Y%m%dT%H%M%S%fZ}-{uuid4().hex[:8]}"
        run_dir = experiment_dir / "runs" / run_id
        run_dir.mkdir(parents=True)
        code_path = run_dir / "analysis.py"
        code_path.write_text(artifact.code, encoding="utf-8")
        environment = {
            "python": sys.version,
            "platform": platform.platform(),
            "code_sha256": hashlib.sha256(artifact.code.encode()).hexdigest(),
            "run_id": run_id,
        }
        (run_dir / "environment.json").write_text(json.dumps(environment, indent=2))
        command = [
            "docker", "run", "--rm", "--network=none", "--read-only",
            "--cpus=2", "--memory=2g", "--pids-limit=256",
            "--security-opt=no-new-privileges", "--cap-drop=ALL",
            "--user=65534:65534", "--tmpfs=/tmp:rw,noexec,nosuid,size=256m",
            "-v", f"{run_dir.resolve()}:/work:rw", "-w", "/work",
            "python:3.11-slim", "python", "analysis.py",
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=self.timeout_seconds,
            env={"PATH": os.environ.get("PATH", "")}, check=False,
        )
        (run_dir / "stdout.log").write_text(result.stdout)
        (run_dir / "stderr.log").write_text(result.stderr)
        (run_dir / "result.json").write_text(json.dumps({"exit_code": result.returncode}, indent=2))
        return run_dir
