#!/usr/bin/env python3
"""Pipeline orchestrator: scans inbox, runs conversions, and coordinates stages."""

import argparse
from pathlib import Path

from scan_pdf import scan_pdf
from extract_modules import extract_modules

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "extract"
SCANNED = ROOT / "synth"
NOTEBOOKS = ROOT / "notebooks"
MODULES = ROOT / "repo"


def run_scan():
    """Scan all new PDFs in the inbox."""
    for pdf in INBOX.glob("*.pdf"):
        md_path = SCANNED / f"{pdf.stem}.md"
        if not md_path.exists():
            print(f"Scanning: {pdf.name}")
            scan_pdf(pdf, SCANNED)


def run_extract():
    """Extract modules from all notebooks."""
    for nb in NOTEBOOKS.glob("*.ipynb"):
        print(f"Extracting from: {nb.name}")
        extract_modules(nb, MODULES)


def main():
    parser = argparse.ArgumentParser(description="Quant research pipeline orchestrator")
    parser.add_argument(
        "stage",
        choices=["scan", "extract", "all"],
        help="Pipeline stage to run",
    )
    args = parser.parse_args()

    if args.stage in ("scan", "all"):
        run_scan()
    if args.stage in ("extract", "all"):
        run_extract()


if __name__ == "__main__":
    main()
