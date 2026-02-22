#!/usr/bin/env python3
"""Extract production code from Jupyter notebooks."""

import argparse
import sys
from pathlib import Path


def extract_modules(notebook_path: Path, output_dir: Path) -> list[Path]:
    """Extract tagged code cells from a notebook into module files."""
    # TODO: Implement notebook to module extraction
    raise NotImplementedError("Module extraction not yet implemented")


def main():
    parser = argparse.ArgumentParser(
        description="Extract production code from notebooks"
    )
    parser.add_argument("notebook", type=Path, help="Path to notebook")
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "repo",
        help="Output directory for extracted modules",
    )
    args = parser.parse_args()

    if not args.notebook.exists():
        print(f"Error: {args.notebook} not found", file=sys.stderr)
        sys.exit(1)

    results = extract_modules(args.notebook, args.output_dir)
    for r in results:
        print(f"Extracted: {r}")


if __name__ == "__main__":
    main()
