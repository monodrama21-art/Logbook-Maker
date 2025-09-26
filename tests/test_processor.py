from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader

from logbook_maker.processor import annotate_pdf


def _create_sample_pdf(path: Path, page_count: int = 3) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(str(path), pagesize=A4)
    for page in range(page_count):
        c.setFont("Helvetica", 14)
        c.drawString(72, 800, f"Original content on page {page + 1}")
        c.showPage()
    c.save()


@pytest.mark.parametrize("page_count", [1, 3])
def test_annotate_pdf_creates_watermarked_output(tmp_path: Path, page_count: int) -> None:
    input_pdf = tmp_path / "input.pdf"
    output_pdf = tmp_path / "output.pdf"
    _create_sample_pdf(input_pdf, page_count)

    annotate_pdf(
        input_pdf,
        output_pdf,
        copy_number="CC-001",
    )

    assert output_pdf.exists()

    reader = PdfReader(str(output_pdf))
    assert len(reader.pages) == page_count

    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        assert "Controlled Copy" in text
        assert "Copy No: CC-001" in text
        assert f"Page {index + 1} / {page_count}" in text


def test_max_pages_limits_processing(tmp_path: Path) -> None:
    input_pdf = tmp_path / "input.pdf"
    output_pdf = tmp_path / "output.pdf"
    _create_sample_pdf(input_pdf, page_count=4)

    annotate_pdf(
        input_pdf,
        output_pdf,
        copy_number="CC-002",
        max_pages=2,
        total_pages=5,
    )

    reader = PdfReader(str(output_pdf))
    assert len(reader.pages) == 4

    first_page_text = reader.pages[0].extract_text() or ""
    third_page_text = reader.pages[2].extract_text() or ""

    assert "Page 1 / 5" in first_page_text
    assert "Copy No: CC-002" in first_page_text

    # Pages beyond the max_pages limit should not have new annotations.
    assert "Copy No: CC-002" not in third_page_text
    assert "Page 3 / 5" not in third_page_text
