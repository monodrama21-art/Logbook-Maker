"""Core functionality for applying watermarks and page numbers to PDFs."""

from __future__ import annotations

import argparse
import io
from pathlib import Path
from typing import Optional

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def annotate_pdf(
    input_pdf: Path | str,
    output_pdf: Path | str,
    *,
    copy_number: str,
    watermark_text: str = "Controlled Copy",
    copy_label_template: str = "Copy No: {copy_number}",
    page_label_template: str = "Page {number} / {total}",
    start_number: int = 1,
    total_pages: Optional[int] = None,
    max_pages: Optional[int] = None,
) -> None:
    """Apply numbering and a watermark to a PDF file.

    Parameters
    ----------
    input_pdf:
        Path to the source PDF.
    output_pdf:
        Path where the annotated PDF will be saved.
    copy_number:
        Identifier printed at the top of each page.
    watermark_text:
        Text placed diagonally across each processed page.
    copy_label_template:
        Template string for rendering the copy number.
    page_label_template:
        Template string for rendering the page number.
    start_number:
        Page number used for the first processed page.
    total_pages:
        Total number of pages displayed in the page label. Defaults to the
        amount of processed pages added to ``start_number`` minus one.
    max_pages:
        Limit of pages to process. Remaining pages are copied without
        annotations.
    """

    input_path = Path(input_pdf)
    output_path = Path(output_pdf)

    if not input_path.exists():
        raise FileNotFoundError(f"Input PDF does not exist: {input_path}")

    if start_number < 1:
        raise ValueError("start_number must be at least 1")

    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    total_page_count = len(reader.pages)

    if max_pages is not None:
        if max_pages < 1:
            raise ValueError("max_pages must be a positive integer")
        processed_page_count = min(max_pages, total_page_count)
    else:
        processed_page_count = total_page_count

    calculated_total = start_number + processed_page_count - 1
    if total_pages is None:
        total_pages = calculated_total
    elif total_pages < calculated_total:
        raise ValueError(
            "total_pages is smaller than the number of pages that will be "
            "numbered."
        )

    for index, page in enumerate(reader.pages):
        if index < processed_page_count:
            current_number = start_number + index
            page_label = page_label_template.format(
                number=current_number, total=total_pages
            )
            copy_label = copy_label_template.format(copy_number=copy_number)
            overlay = _build_overlay_page(
                page.mediabox.width,
                page.mediabox.height,
                page_label,
                copy_label,
                watermark_text,
            )
            page.merge_page(overlay)
        writer.add_page(page)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as file_out:
        writer.write(file_out)


def _build_overlay_page(
    width: float,
    height: float,
    page_label: str,
    copy_label: str,
    watermark_text: str,
):
    """Create an overlay PDF page with the provided labels."""

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(float(width), float(height)))

    margin = 0.6 * inch

    # Copy number at the top-right corner.
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawRightString(float(width) - margin, float(height) - margin, copy_label)

    # Page number at the bottom centre.
    c.setFont("Helvetica", 12)
    c.drawCentredString(float(width) / 2.0, margin / 2.0, page_label)

    # Watermark diagonally across the page.
    c.saveState()
    c.setFillColor(colors.Color(0.7, 0.7, 0.7, alpha=0.2))
    c.setFont("Helvetica-Bold", min(float(width), float(height)) * 0.1)
    c.translate(float(width) / 2.0, float(height) / 2.0)
    c.rotate(45)
    c.drawCentredString(0, 0, watermark_text)
    c.restoreState()

    c.save()
    packet.seek(0)
    overlay_reader = PdfReader(packet)
    return overlay_reader.pages[0]


def build_argument_parser() -> argparse.ArgumentParser:
    """Return an argument parser configured for the CLI."""

    parser = argparse.ArgumentParser(
        description=(
            "Add page numbers and a Controlled Copy watermark to a PDF file."
        )
    )
    parser.add_argument("input_pdf", type=Path, help="Path to the source PDF")
    parser.add_argument(
        "output_pdf", type=Path, help="Where the annotated PDF will be saved"
    )
    parser.add_argument(
        "--copy-number",
        required=True,
        help="Identifier displayed on every page",
    )
    parser.add_argument(
        "--watermark-text",
        default="Controlled Copy",
        help="Text used as a diagonal watermark",
    )
    parser.add_argument(
        "--copy-label-template",
        default="Copy No: {copy_number}",
        help="Template for the copy number label",
    )
    parser.add_argument(
        "--page-label-template",
        default="Page {number} / {total}",
        help="Template for the page numbering label",
    )
    parser.add_argument(
        "--start-number",
        type=int,
        default=1,
        help="Number used for the first processed page",
    )
    parser.add_argument(
        "--total-pages",
        type=int,
        help="Explicit total used in the page label",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Limit how many pages from the start of the PDF are processed",
    )
    return parser


def main(args: Optional[list[str]] = None) -> None:
    """Entry point for the command-line interface."""

    parser = build_argument_parser()
    parsed = parser.parse_args(args=args)
    annotate_pdf(
        parsed.input_pdf,
        parsed.output_pdf,
        copy_number=parsed.copy_number,
        watermark_text=parsed.watermark_text,
        copy_label_template=parsed.copy_label_template,
        page_label_template=parsed.page_label_template,
        start_number=parsed.start_number,
        total_pages=parsed.total_pages,
        max_pages=parsed.max_pages,
    )


if __name__ == "__main__":
    main()
