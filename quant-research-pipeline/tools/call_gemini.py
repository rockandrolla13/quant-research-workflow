#!/usr/bin/env python3
"""Unified Gemini API wrapper. Three modes: extract, review, verify-tex."""

from pathlib import Path

import typer
from dotenv import load_dotenv
from google import genai
from google.genai import types
from rich.console import Console

load_dotenv()

console = Console()
app = typer.Typer()

MODEL = "gemini-2.5-flash"


def _client() -> genai.Client:
    return genai.Client()


def extract_pdf(pdf_path: str, output_path: str) -> str:
    """Mode: extract — PDF bytes → structured markdown."""
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    response = _client().models.generate_content(
        model=MODEL,
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

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    return response.text


def review_spec(spec_path: str, formula_path: str, output_path: str) -> str:
    """Mode: review — spec.yaml + formula.md → structured checklist."""
    spec_content = Path(spec_path).read_text(encoding="utf-8")
    formula_content = Path(formula_path).read_text(encoding="utf-8")

    response = _client().models.generate_content(
        model=MODEL,
        contents=[
            f"## spec.yaml\n```yaml\n{spec_content}\n```\n\n"
            f"## formula.md\n{formula_content}",
            """You are a mathematical reviewer for a quantitative trading strategy.
Review for:
1. Every symbol in formula.md appears in spec.yaml signal.inputs or parameters
2. formula_latex fields are syntactically valid LaTeX
3. Signal definition is self-consistent (dimensions match, no circular refs)
4. Test cases are consistent with the formulas
5. Data frequencies are compatible with signal computation
6. Any unstated assumptions

Output format (use EXACTLY this structure):
## Review: spec.yaml + formula.md
### Symbol Consistency
- [ ] PASS/WARN/FAIL: [description]
### LaTeX Validity
- [ ] PASS/WARN/FAIL: [description]
### Dimensional Consistency
- [ ] PASS/WARN/FAIL: [description]
### Test Case Consistency
- [ ] PASS/WARN/FAIL: [description]
### Data Frequency Compatibility
- [ ] PASS/WARN/FAIL: [description]
### Unstated Assumptions
- [ ] WARN: [description] — suggested addition: ...
### Summary
PASS / PASS WITH WARNINGS / FAIL
[1-2 sentence summary]""",
        ],
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    return response.text


def verify_tex(tex_path: str, output_path: str) -> str:
    """Mode: verify-tex — .tex file → compilation + notation check."""
    tex_content = Path(tex_path).read_text(encoding="utf-8")

    response = _client().models.generate_content(
        model=MODEL,
        contents=[
            f"```latex\n{tex_content}\n```",
            """Review this LaTeX document:
1. All equations syntactically correct (will compile)
2. Notation consistent throughout (same symbol = same meaning)
3. No missing closing delimiters
4. All \\ref and \\label pairs match
5. All \\cite keys have bibliography entries
Output checklist with PASS/FAIL per item. If FAIL, give exact line + fix.""",
        ],
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    return response.text


@app.command()
def main(
    mode: str = typer.Option(..., "--mode", "-m", help="extract | review | verify-tex"),
    pdf: Path = typer.Option(None, "--pdf", help="PDF path (extract mode)"),
    spec: Path = typer.Option(None, "--spec", help="spec.yaml path (review mode)"),
    formula: Path = typer.Option(None, "--formula", help="formula.md path (review mode)"),
    tex: Path = typer.Option(None, "--tex", help=".tex path (verify-tex mode)"),
    output: Path = typer.Option(..., "--output", "-o", help="Output file path"),
) -> None:
    """Unified Gemini API wrapper with three modes."""
    output.parent.mkdir(parents=True, exist_ok=True)

    if mode == "extract":
        if not pdf or not pdf.exists():
            console.print("[red]❌ --pdf required and must exist for extract mode[/red]")
            raise typer.Exit(code=1)
        console.print(f"[cyan]⏳ Extracting {pdf}...[/cyan]")
        text = extract_pdf(str(pdf), str(output))
        console.print(f"[green]✅ Extracted {len(text)} chars → {output}[/green]")

    elif mode == "review":
        if not spec or not spec.exists():
            console.print("[red]❌ --spec required and must exist for review mode[/red]")
            raise typer.Exit(code=1)
        if not formula or not formula.exists():
            console.print("[red]❌ --formula required and must exist for review mode[/red]")
            raise typer.Exit(code=1)
        console.print("[cyan]⏳ Reviewing spec + formula...[/cyan]")
        text = review_spec(str(spec), str(formula), str(output))
        console.print(f"[green]✅ Review written → {output}[/green]")

    elif mode == "verify-tex":
        if not tex or not tex.exists():
            console.print("[red]❌ --tex required and must exist for verify-tex mode[/red]")
            raise typer.Exit(code=1)
        console.print(f"[cyan]⏳ Verifying {tex}...[/cyan]")
        text = verify_tex(str(tex), str(output))
        console.print(f"[green]✅ Verification written → {output}[/green]")

    else:
        console.print(f"[red]❌ Unknown mode: {mode}. Use extract|review|verify-tex[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
