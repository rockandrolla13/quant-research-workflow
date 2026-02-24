#!/usr/bin/env python3
"""PDF → extract/raw.md (Marker + Gemini fallback)."""

import json
from datetime import datetime, timezone
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()
app = typer.Typer()


def _avg_chars(pdf: Path) -> float:
    from pypdf import PdfReader
    pages = PdfReader(str(pdf)).pages
    if not pages:
        console.print("[red]❌ PDF has 0 pages[/red]")
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


def _extract_gemini(pdf: Path) -> tuple[str, int]:
    from google import genai
    from google.genai import types
    from pypdf import PdfReader

    resp = genai.Client().models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=pdf.read_bytes(), mime_type="application/pdf"),
            """Convert PDF to markdown. Preserve ALL equations ($$/$), tables, headings, figures. Extract EVERYTHING.""",
        ],
    )
    return resp.text, len(PdfReader(str(pdf)).pages)


@app.command()
def ingest(
    pdf_path: Path = typer.Argument(..., help="Source PDF"),
    strategy_id: str = typer.Option(None, "-s", "--strategy-id"),
) -> None:
    if not pdf_path.exists():
        console.print(f"[red]❌ Not found: {pdf_path}[/red]")
        raise typer.Exit(1)

    sid = strategy_id or pdf_path.stem
    root = Path(__file__).resolve().parent.parent
    strat_dir = root / "strategies" / sid
    extract_dir = strat_dir / "extract"
    for d in [strat_dir / "input", extract_dir, extract_dir / "images"]:
        d.mkdir(parents=True, exist_ok=True)

    dest = strat_dir / "input/source.pdf"
    if not dest.exists():
        import shutil
        shutil.copy2(pdf_path, dest)
        console.print(f"📄 Copied → {dest}")

    avg = _avg_chars(pdf_path)
    scanned = avg < 100
    console.print(f"📊 {avg:.0f} chars/page → {'Gemini' if scanned else 'Marker'}")

    method, warnings, text, pages = "marker", [], "", 0
    out = extract_dir / "raw.md"

    if not scanned:
        try:
            console.print("[cyan]⏳ Marker...[/cyan]")
            text, pages = _extract_marker(pdf_path, extract_dir)
        except Exception as e:
            warnings.append(f"Marker: {e}")
            console.print(f"[yellow]⚠️ Marker failed: {e}[/yellow]")
            scanned = True

    if scanned or not text:
        try:
            console.print("[cyan]⏳ Gemini...[/cyan]")
            text, pages = _extract_gemini(pdf_path)
            method = "gemini"
        except Exception as e:
            console.print(f"[red]❌ Gemini failed: {e}[/red]")
            out.unlink(missing_ok=True)
            raise typer.Exit(1)

    out.write_text(text, encoding="utf-8")
    (extract_dir / "extract_report.json").write_text(json.dumps({
        "strategy_id": sid, "method": method, "pages": pages,
        "avg_chars": round(avg, 1), "scanned": scanned,
        "warnings": warnings, "timestamp": datetime.now(timezone.utc).isoformat(),
    }, indent=2))
    (extract_dir / ".done").touch()

    console.print(f"[green]✅ {sid}: {len(text)} chars, {pages} pages ({method})[/green]")


if __name__ == "__main__":
    app()
