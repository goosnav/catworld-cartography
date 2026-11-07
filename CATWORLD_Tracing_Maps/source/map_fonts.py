"""Portable serif fonts for the tracing sheets and guide."""
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import Font


def register_fonts():
    # Standard PDF fonts are available on every platform and remain vector text.
    for name, face in [('Book', 'Times-Roman'), ('Italic', 'Times-Italic'),
                       ('Bold', 'Times-Bold')]:
        pdfmetrics.registerFont(Font(name, face, 'WinAnsiEncoding'))
