#!/usr/bin/env python3
"""PDF to Markdown conversion script."""

import argparse
import sys
from pathlib import Path


import fitz  # PyMuPDF

def scan_pdf(pdf_path: Path, output_dir: Path) -> Path:
    """Convert a PDF file to markdown."""
    output_path = output_dir / f"{pdf_path.stem}.md"
    
    markdown_content = []
    try:
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            markdown_content.append(f"# Page {page_num + 1}\n\n")
            text = page.get_text("text")
            markdown_content.append(text)
            markdown_content.append("\n\n")
        doc.close()

        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("".join(markdown_content))
        
        return output_path
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown")
    parser.add_argument("pdf", type=Path, help="Path to PDF file")
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "extract",
        help="Output directory for markdown files",
    )
    args = parser.parse_args()

    if not args.pdf.exists():
        print(f"Error: {args.pdf} not found", file=sys.stderr)
        sys.exit(1)

    result = scan_pdf(args.pdf, args.output_dir)
    print(f"Saved: {result}")


if __name__ == "__main__":
    main()
