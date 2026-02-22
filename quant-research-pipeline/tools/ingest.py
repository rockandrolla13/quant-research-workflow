#!/usr/bin/env python3
"""PDF → extract/raw.md (Marker + Gemini fallback)."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()

console = Console()
app = typer.Typer()


def _avg_chars_per_page(pdf_path: Path) -> float:
    """Detect scanned vs text-layer PDF using pypdf."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    if len(reader.pages) == 0:
        console.print("[red]❌ PDF has 0 pages[/red]")
        raise typer.Exit(code=1)
    total_chars = sum(len((p.extract_text() or "")) for p in reader.pages)
    return total_chars / len(reader.pages)


def _extract_marker(pdf_path: Path, extract_dir: Path) -> tuple[str, int]:
    """Marker route: high-quality PDF→MD with layout and OCR."""
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered

    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(str(pdf_path))
    text, _, images = text_from_rendered(rendered)

    # Save images
    images_dir = extract_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    for img_name, img_data in (images or {}).items():
        (images_dir / img_name).write_bytes(img_data)

    page_count = text.count("\n# Page ") or text.count("\n---") or 1
    return text, page_count


def _extract_gemini(pdf_path: Path, output_path: Path) -> tuple[str, int]:
    """Gemini route: send PDF bytes directly to the API."""
    from google import genai
    from google.genai import types

    client = genai.Client()

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            """Convert this entire PDF to structured markdown.
Rules:
- Preserve ALL equations as LaTeX blocks ($$ for display, $ for inline)
- Preserve ALL tables as markdown tables
- Preserve section headings with proper # hierarchy
- Preserve figure captions as > blockquotes
- Preserve numbered references
- Do NOT summarise or omit content — extract EVERYTHING
- For image-only pages: [Figure: brief description]
- Keep original equation numbers if present""",
        ],
    )

    text = response.text
    from pypdf import PdfReader

    page_count = len(PdfReader(str(pdf_path)).pages)
    return text, page_count


@app.command()
def ingest(
    pdf_path: Path = typer.Argument(..., help="Path to source PDF"),
    strategy_id: str = typer.Option(
        None, "--strategy-id", "-s", help="Strategy ID (defaults to PDF stem)"
    ),
) -> None:
    """Convert a PDF into structured markdown at extract/raw.md."""
    if not pdf_path.exists():
        console.print(f"[red]❌ PDF not found: {pdf_path}[/red]")
        raise typer.Exit(code=1)

    sid = strategy_id or pdf_path.stem
    root = Path(__file__).resolve().parent.parent
    strategy_dir = root / "strategies" / sid

    # Create directories
    input_dir = strategy_dir / "input"
    extract_dir = strategy_dir / "extract"
    images_dir = extract_dir / "images"
    for d in [input_dir, extract_dir, images_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Copy PDF to input/
    dest_pdf = input_dir / "source.pdf"
    if not dest_pdf.exists():
        import shutil

        shutil.copy2(pdf_path, dest_pdf)
        console.print(f"📄 Copied PDF to {dest_pdf}")

    output_path = extract_dir / "raw.md"

    # Detect scanned vs text-layer
    avg_chars = _avg_chars_per_page(pdf_path)
    scanned = avg_chars < 100
    console.print(
        f"📊 Avg chars/page: {avg_chars:.0f} → {'scanned (Gemini)' if scanned else 'text-layer (Marker)'}"
    )

    method = "gemini" if scanned else "marker"
    warnings = []
    text = ""
    pages = 0

    if not scanned:
        # Try Marker first
        try:
            console.print("[cyan]⏳ Running Marker...[/cyan]")
            text, pages = _extract_marker(pdf_path, extract_dir)
            method = "marker"
        except Exception as e:
            warnings.append(f"Marker failed: {e}")
            console.print(f"[yellow]⚠️  Marker failed, falling back to Gemini: {e}[/yellow]")
            scanned = True  # force Gemini fallback

    if scanned or not text:
        # Gemini route
        try:
            console.print("[cyan]⏳ Running Gemini extraction...[/cyan]")
            text, pages = _extract_gemini(pdf_path, output_path)
            method = "gemini"
        except Exception as e:
            console.print(f"[red]❌ Gemini extraction failed: {e}[/red]")
            # Do NOT produce partial raw.md
            if output_path.exists():
                output_path.unlink()
            raise typer.Exit(code=1)

    # Write raw.md
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Write extract_report.json
    report = {
        "strategy_id": sid,
        "method": method,
        "pages_processed": pages,
        "avg_chars_per_page": round(avg_chars, 1),
        "scanned_detected": avg_chars < 100,
        "warnings": warnings,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    report_path = extract_dir / "extract_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Touch .done signal
    (extract_dir / ".done").touch()

    console.print(f"[green]✅ {sid}: extract/raw.md written ({len(text)} chars, {pages} pages, method={method})[/green]")


if __name__ == "__main__":
    app()
