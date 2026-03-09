#!/usr/bin/env python3
"""PDF → extract/raw.md (pass 1: OCR) + artifacts/01-extraction.md (pass 2: tagged)."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()
app = typer.Typer()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

_TAG_PROMPT = """You are extracting a quantitative research paper for implementation as a trading strategy.
This is a sell-side quant research paper (DB, JPM, or similar).

Tag every extractable element with the appropriate label:

| Tag | Use for |
|-----|---------|
| [SIG:n] | Signal definitions (entry/exit rules, alpha factors) |
| [EQ:n] | Equations — preserve LaTeX notation |
| [PORT:n] | Portfolio construction rules (weighting, rebalancing) |
| [RISK:n] | Risk controls and constraints |
| [DATA:n] | Data requirements, schemas, sources |
| [ASSUMP:n] | Assumptions and constraints stated by authors |
| [PARAM:n] | Parameters, hyperparameters, tunable constants |
| [TABLE:n] | Tables — reproduce as markdown tables |
| [FIG:n] | Figures — describe content, note what they show |
| [PERF:n] | Reported performance metrics |

Rules:
1. Preserve ALL equations as LaTeX ($$ for display, $ for inline)
2. Preserve ALL tables as markdown tables
3. Preserve section headings with # hierarchy matching the paper
4. Do NOT summarise — extract EVERYTHING
5. Tag elements inline where they appear in the text
6. Number tags sequentially within each type (EQ:1, EQ:2, ...)
7. If an element fits multiple tags, use the most specific one

Begin with a YAML metadata block:
```yaml
---
title: "<paper title>"
authors: [<author list>]
date: "<publication date>"
source: "<institution>"
pages: <n>
tags_found:
  SIG: <count>
  EQ: <count>
  PORT: <count>
  RISK: <count>
  DATA: <count>
  ASSUMP: <count>
  PARAM: <count>
  TABLE: <count>
  FIG: <count>
  PERF: <count>
---
```

Then the full paper content with tags, preserving the paper's section structure."""


def _avg_chars(pdf: Path) -> float:
    from pypdf import PdfReader
    pages = PdfReader(str(pdf)).pages
    if not pages:
        console.print("[red]PDF has 0 pages[/red]")
        raise typer.Exit(1)
    return sum(len(p.extract_text() or "") for p in pages) / len(pages)


def _extract_marker(pdf: Path, extract_dir: Path) -> tuple[str, int]:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered

    text, _, images = text_from_rendered(PdfConverter(artifact_dict=create_model_dict())(str(pdf)))
    img_dir = extract_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    for name, data in (images or {}).items():
        (img_dir / name).write_bytes(data)
    return text, text.count("\n# Page ") or text.count("\n---") or 1


def _extract_gemini_raw(pdf: Path) -> tuple[str, int]:
    from google import genai
    from google.genai import types
    from pypdf import PdfReader

    resp = genai.Client().models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=pdf.read_bytes(), mime_type="application/pdf"),
            "Convert PDF to markdown. Preserve ALL equations ($$/$), tables, headings, figures. Extract EVERYTHING.",
        ],
    )
    return resp.text, len(PdfReader(str(pdf)).pages)


def _tag_extraction(pdf: Path) -> str:
    """Pass 2: Gemini reads the PDF and produces tagged structured extraction."""
    from google import genai
    from google.genai import types

    resp = genai.Client().models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=pdf.read_bytes(), mime_type="application/pdf"),
            _TAG_PROMPT,
        ],
    )
    return resp.text


@app.command()
def ingest(
    pdf_path: Path = typer.Argument(..., help="Source PDF"),
    strategy_id: str = typer.Option(None, "-s", "--strategy-id"),
    skip_tagging: bool = typer.Option(False, "--skip-tagging", help="Skip pass 2 (tagged extraction)"),
) -> None:
    if not pdf_path.exists():
        console.print(f"[red]Not found: {pdf_path}[/red]")
        raise typer.Exit(1)

    sid = strategy_id or pdf_path.stem
    root = Path(__file__).resolve().parent.parent
    strat_dir = root / "strategies" / sid
    extract_dir = strat_dir / "extract"
    artifacts_dir = strat_dir / "artifacts"
    for d in [strat_dir / "input", extract_dir, extract_dir / "images", artifacts_dir]:
        d.mkdir(parents=True, exist_ok=True)

    dest = strat_dir / "input/source.pdf"
    if not dest.exists():
        import shutil
        shutil.copy2(pdf_path, dest)
        console.print(f"Copied -> {dest}")

    avg = _avg_chars(pdf_path)
    scanned = avg < 100
    console.print(f"{avg:.0f} chars/page -> {'Gemini' if scanned else 'Marker'}")

    # --- Pass 1: Raw extraction (OCR/layout) ---
    method, warnings, text, pages = "marker", [], "", 0
    raw_out = extract_dir / "raw.md"

    if not scanned:
        try:
            console.print("[cyan]Pass 1: Marker...[/cyan]")
            text, pages = _extract_marker(pdf_path, extract_dir)
        except Exception as e:
            warnings.append(f"Marker: {e}")
            console.print(f"[yellow]Marker failed: {e}[/yellow]")
            scanned = True

    if scanned or not text:
        try:
            console.print("[cyan]Pass 1: Gemini raw...[/cyan]")
            text, pages = _extract_gemini_raw(pdf_path)
            method = "gemini"
        except Exception as e:
            console.print(f"[red]Gemini failed: {e}[/red]")
            raw_out.unlink(missing_ok=True)
            raise typer.Exit(1)

    raw_out.write_text(text, encoding="utf-8")
    console.print(f"[green]Pass 1 done: {len(text)} chars, {pages} pages ({method})[/green]")

    # --- Pass 2: Tagged structured extraction ---
    tagged_out = artifacts_dir / "01-extraction.md"
    if not skip_tagging:
        try:
            console.print("[cyan]Pass 2: Tagged extraction...[/cyan]")
            tagged_text = _tag_extraction(pdf_path)
            tagged_out.write_text(tagged_text, encoding="utf-8")
            console.print(f"[green]Pass 2 done: {len(tagged_text)} chars -> {tagged_out.name}[/green]")
        except Exception as e:
            warnings.append(f"Tagging: {e}")
            console.print(f"[yellow]Tagging failed: {e} — raw extraction available[/yellow]")

    # --- Report ---
    (extract_dir / "extract_report.json").write_text(json.dumps({
        "strategy_id": sid, "method": method, "pages": pages,
        "avg_chars": round(avg, 1), "scanned": scanned,
        "tagged": tagged_out.exists(),
        "warnings": warnings, "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2))
    (extract_dir / ".done").touch()

    console.print(f"[green]{sid}: extraction complete[/green]")


if __name__ == "__main__":
    app()
