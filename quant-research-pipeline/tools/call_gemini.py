#!/usr/bin/env python3
"""Gemini API wrapper: extract, review, verify-tex modes."""

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
_client_cache: genai.Client | None = None


def _client() -> genai.Client:
    global _client_cache
    if _client_cache is None:
        _client_cache = genai.Client()
    return _client_cache


def _write(path: str, text: str) -> str:
    Path(path).write_text(text, encoding="utf-8")
    return text


def extract_pdf(pdf_path: str, output_path: str) -> str:
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    resp = _client().models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            """Convert this PDF to structured markdown.
- Preserve ALL equations as LaTeX ($$ display, $ inline)
- Preserve ALL tables as markdown tables
- Preserve section headings with # hierarchy
- Preserve figure captions as > blockquotes
- Do NOT summarise — extract EVERYTHING""",
        ],
    )
    return _write(output_path, resp.text)


def review_spec(spec_path: str, formula_path: str, output_path: str) -> str:
    spec = Path(spec_path).read_text(encoding="utf-8")
    formula = Path(formula_path).read_text(encoding="utf-8")
    resp = _client().models.generate_content(
        model=MODEL,
        contents=[
            f"## spec.yaml\n```yaml\n{spec}\n```\n\n## formula.md\n{formula}",
            """Mathematical reviewer for quant strategy.

If formula.md has "## Scope", only review IN-SCOPE formulas.

Review: 1) Symbol consistency 2) LaTeX validity 3) Dimensional consistency
4) Test case consistency 5) Data frequency compatibility 6) Unstated assumptions

Use WARN-BLOCKING for must-fix issues, WARN-COSMETIC for suggestions.

Output:
## Review: spec.yaml + formula.md
### Symbol Consistency
- [ ] PASS/WARN-BLOCKING/WARN-COSMETIC/FAIL: [description]
### LaTeX Validity
- [ ] PASS/WARN-BLOCKING/WARN-COSMETIC/FAIL: [description]
### Dimensional Consistency
- [ ] PASS/WARN-BLOCKING/WARN-COSMETIC/FAIL: [description]
### Test Case Consistency
- [ ] PASS/WARN-BLOCKING/WARN-COSMETIC/FAIL: [description]
### Data Frequency Compatibility
- [ ] PASS/WARN-BLOCKING/WARN-COSMETIC/FAIL: [description]
### Unstated Assumptions
- [ ] WARN-BLOCKING/WARN-COSMETIC: [description]
### Summary
PASS / PASS WITH COSMETIC WARNINGS / FAIL
[1-2 sentence summary]""",
        ],
    )
    return _write(output_path, resp.text)


def verify_tex(tex_path: str, output_path: str, bib_path: str | None = None) -> str:
    tex = Path(tex_path).read_text(encoding="utf-8")
    content = f"```latex\n{tex}\n```"
    if bib_path:
        bib = Path(bib_path).read_text(encoding="utf-8")
        content += f"\n## Bibliography\n```bibtex\n{bib}\n```"
    resp = _client().models.generate_content(
        model=MODEL,
        contents=[
            content,
            """Review LaTeX:
1. Equations syntactically correct
2. Notation consistent
3. No missing delimiters
4. \\ref/\\label pairs match
5. \\cite keys have bib entries
Output PASS/FAIL per item. If FAIL, give line + fix.""",
        ],
    )
    return _write(output_path, resp.text)


@app.command()
def main(
    mode: str = typer.Option(..., "--mode", "-m", help="extract|review|verify-tex"),
    pdf: Path = typer.Option(None, "--pdf"),
    spec: Path = typer.Option(None, "--spec"),
    formula: Path = typer.Option(None, "--formula"),
    tex: Path = typer.Option(None, "--tex"),
    bib: Path = typer.Option(None, "--bib"),
    output: Path = typer.Option(..., "--output", "-o"),
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    if mode == "extract":
        if not pdf or not pdf.exists():
            console.print("[red]❌ --pdf required[/red]")
            raise typer.Exit(1)
        console.print(f"[cyan]⏳ Extracting {pdf}...[/cyan]")
        text = extract_pdf(str(pdf), str(output))
        console.print(f"[green]✅ {len(text)} chars → {output}[/green]")

    elif mode == "review":
        if not spec or not spec.exists() or not formula or not formula.exists():
            console.print("[red]❌ --spec and --formula required[/red]")
            raise typer.Exit(1)
        console.print("[cyan]⏳ Reviewing...[/cyan]")
        review_spec(str(spec), str(formula), str(output))
        console.print(f"[green]✅ Review → {output}[/green]")

    elif mode == "verify-tex":
        if not tex or not tex.exists():
            console.print("[red]❌ --tex required[/red]")
            raise typer.Exit(1)
        bib_p = str(bib) if bib and bib.exists() else None
        console.print(f"[cyan]⏳ Verifying {tex}...[/cyan]")
        verify_tex(str(tex), str(output), bib_p)
        console.print(f"[green]✅ Verified → {output}[/green]")

    else:
        console.print(f"[red]❌ Unknown mode: {mode}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
