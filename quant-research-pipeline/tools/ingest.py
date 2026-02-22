#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv # Import load_dotenv
from google import genai

load_dotenv() # Load environment variables from .env file

# The new implementation of ingest.py does not use scan_pdf, so we can remove the path modification and import
# sys.path.append(str(Path(__file__).resolve().parent))
# from scan_pdf import scan_pdf


def main():
    parser = argparse.ArgumentParser(description="Ingest a PDF, process with Gemini, and save raw output.")
    parser.add_argument("pdf", type=Path, help="Path to PDF file to ingest.")
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "extract",
        help="Output directory for raw Gemini output (raw.md).",
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="gemini-2.5-flash", # Changed default to 'gemini-2.5-flash' as per user instruction
        help="Gemini model to use (e.g., 'gemini-2.5-flash').",
    )
    args = parser.parse_args()

    if not args.pdf.exists():
        print(f"Error: PDF file not found at {args.pdf}", file=sys.stderr)
        sys.exit(1)

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw_output_path = args.output_dir / "raw.md"

    print(f"Processing PDF with Gemini model: {args.model}")

    try:
        client = genai.Client()
        with open(args.pdf, 'rb') as f:
            response = client.models.generate_content(
                model=args.model,
                contents=[
                    genai.types.Part.from_bytes(data=f.read(), mime_type='application/pdf'),
                    'Convert this PDF to structured markdown. Preserve all equations as LaTeX blocks. Preserve all tables.'
                ]
            )
        raw_md = response.text
    except Exception as e:
        print(f"Failed to process PDF with Gemini: {e}", file=sys.stderr)
        sys.exit(1)

    # Save Gemini's raw output
    with open(raw_output_path, "w", encoding="utf-8") as f:
        f.write(raw_md)

    print(f"Successfully ingested {args.pdf} and saved raw Gemini output to {raw_output_path}")


if __name__ == "__main__":
    main()
