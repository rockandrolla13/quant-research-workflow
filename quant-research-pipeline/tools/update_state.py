#!/usr/bin/env python3
"""Rebuild .pipeline_state.yaml from filesystem artifacts."""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer()


def _exists(p: Path, min_chars: int = 0) -> bool:
    return p.exists() and p.stat().st_size > min_chars


def _run(cmd: list, timeout: int = 10) -> bool:
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout).returncode == 0
    except Exception:
        return False


def _check_ingest(d: Path) -> bool:
    return _exists(d / "extract/raw.md", 500) and (d / "extract/.done").exists()


def _check_synth(d: Path) -> bool:
    return _exists(d / "synth/strategy.md") and _exists(d / "synth/formula.md")


def _check_spec(d: Path) -> bool:
    spec = d / "spec/spec.yaml"
    if not spec.exists():
        return False
    validator = Path(__file__).resolve().parent / "validate_spec.py"
    return _run([sys.executable, str(validator), str(spec)])


def _check_spec_review(d: Path) -> bool:
    return _exists(d / "spec/review.md")


def _check_spec_lock(d: Path) -> bool:
    result = subprocess.run(["git", "tag", "-l", f"spec-{d.name}-*"],
                            capture_output=True, text=True, timeout=5)
    return bool(result.stdout.strip())


def _check_implement(d: Path) -> bool:
    return (d / "repo/src" / d.name / "__init__.py").exists()


def _check_test(d: Path) -> bool:
    tests = d / "repo/tests"
    if not tests.exists() or not list(tests.glob("test_*.py")):
        return False
    root = Path(__file__).resolve().parent.parent
    py = root / ".venv-stratpipe/bin/python"
    exe = str(py) if py.exists() else sys.executable
    return _run([exe, "-m", "pytest", str(tests), "-q", "--tb=no"], timeout=120)


def _check_tex(d: Path) -> bool:
    return _exists(d / "tex/note.tex")


def _check_package(d: Path) -> bool:
    return _exists(d / "repo/pyproject.toml")


STAGES = [
    ("ingest", _check_ingest), ("synth", _check_synth), ("spec", _check_spec),
    ("spec_review", _check_spec_review), ("spec_lock", _check_spec_lock),
    ("implement", _check_implement), ("test", _check_test),
    ("tex", _check_tex), ("package", _check_package),
]


def build_state(d: Path) -> dict:
    return {
        "strategy_id": d.name,
        "stages": {
            name: {"status": "done" if fn(d) else "pending",
                   "checked_at": datetime.now(timezone.utc).isoformat()}
            for name, fn in STAGES
        }
    }


@app.command()
def update(
    strategy_dir: Path = typer.Argument(..., help="Strategy directory"),
    status: bool = typer.Option(False, "--status", help="Print only"),
) -> None:
    if not strategy_dir.exists():
        console.print(f"[red]❌ Not found: {strategy_dir}[/red]")
        raise typer.Exit(code=1)

    state = build_state(strategy_dir)
    if not status:
        (strategy_dir / ".pipeline_state.yaml").write_text(
            yaml.dump(state, default_flow_style=False, sort_keys=False))
        console.print(f"📝 State written")

    table = Table(title=f"Pipeline: {strategy_dir.name}")
    table.add_column("Stage", style="bold")
    table.add_column("Status")
    for name, _ in STAGES:
        s = state["stages"][name]["status"]
        table.add_row(name, f"{'✅' if s == 'done' else '❌'} {s}")
    console.print(table)


if __name__ == "__main__":
    app()
