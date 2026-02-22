#!/usr/bin/env python3
"""Rebuild .pipeline_state.yaml from filesystem artifacts.

This file is DERIVED, never hand-edited.
"""

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


def _file_exists_and_nonempty(p: Path, min_chars: int = 0) -> bool:
    return p.exists() and p.stat().st_size > min_chars


def _check_ingest(strategy_dir: Path) -> bool:
    raw = strategy_dir / "extract" / "raw.md"
    done = strategy_dir / "extract" / ".done"
    return _file_exists_and_nonempty(raw, min_chars=500) and done.exists()


def _check_synth(strategy_dir: Path) -> bool:
    strat = strategy_dir / "synth" / "strategy.md"
    form = strategy_dir / "synth" / "formula.md"
    return _file_exists_and_nonempty(strat) and _file_exists_and_nonempty(form)


def _check_spec(strategy_dir: Path) -> bool:
    spec_yaml = strategy_dir / "spec" / "spec.yaml"
    if not spec_yaml.exists():
        return False
    validate_script = Path(__file__).resolve().parent / "validate_spec.py"
    try:
        result = subprocess.run(
            [sys.executable, str(validate_script), str(spec_yaml)],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def _check_spec_review(strategy_dir: Path) -> bool:
    return _file_exists_and_nonempty(strategy_dir / "spec" / "review.md")


def _check_spec_lock(strategy_dir: Path) -> bool:
    sid = strategy_dir.name
    try:
        result = subprocess.run(
            ["git", "tag", "-l", f"spec-{sid}-*"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def _check_implement(strategy_dir: Path) -> bool:
    sid = strategy_dir.name
    init = strategy_dir / "repo" / "src" / sid / "__init__.py"
    return init.exists()


def _check_test(strategy_dir: Path) -> bool:
    test_dir = strategy_dir / "repo" / "tests"
    if not test_dir.exists():
        return False
    test_files = list(test_dir.glob("test_*.py"))
    if not test_files:
        return False
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_dir), "-q", "--tb=no"],
            capture_output=True,
            timeout=120,
        )
        return result.returncode == 0
    except Exception:
        return False


def _check_tex(strategy_dir: Path) -> bool:
    return _file_exists_and_nonempty(strategy_dir / "tex" / "note.tex")


def _check_package(strategy_dir: Path) -> bool:
    return _file_exists_and_nonempty(strategy_dir / "repo" / "pyproject.toml")


STAGES = [
    ("ingest", _check_ingest),
    ("synth", _check_synth),
    ("spec", _check_spec),
    ("spec_review", _check_spec_review),
    ("spec_lock", _check_spec_lock),
    ("implement", _check_implement),
    ("test", _check_test),
    ("tex", _check_tex),
    ("package", _check_package),
]


def build_state(strategy_dir: Path) -> dict:
    state = {"strategy_id": strategy_dir.name, "stages": {}}
    for name, check_fn in STAGES:
        passed = check_fn(strategy_dir)
        state["stages"][name] = {
            "status": "done" if passed else "pending",
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
    return state


@app.command()
def update(
    strategy_dir: Path = typer.Argument(..., help="Path to strategy directory"),
    status: bool = typer.Option(False, "--status", help="Print-only, don't write state file"),
) -> None:
    """Rebuild .pipeline_state.yaml from filesystem artifacts."""
    if not strategy_dir.exists():
        console.print(f"[red]❌ Directory not found: {strategy_dir}[/red]")
        raise typer.Exit(code=1)

    state = build_state(strategy_dir)

    if not status:
        state_path = strategy_dir / ".pipeline_state.yaml"
        with open(state_path, "w", encoding="utf-8") as f:
            yaml.dump(state, f, default_flow_style=False, sort_keys=False)
        console.print(f"📝 State written to {state_path}")

    # Print table
    table = Table(title=f"Pipeline State: {strategy_dir.name}")
    table.add_column("Stage", style="bold")
    table.add_column("Status")

    for name, _ in STAGES:
        s = state["stages"][name]["status"]
        icon = "✅" if s == "done" else "❌"
        table.add_row(name, f"{icon} {s}")

    console.print(table)


if __name__ == "__main__":
    app()
