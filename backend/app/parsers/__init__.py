"""
Модуль парсеров для различных форматов файлов.
Адаптировано из проекта analyse-text.
"""

from .txt_parser import TxtParser, parse_txt_file, validate_txt_file
from .fb2_parser import FB2Parser, parse_fb2_file, validate_fb2_file
from .pdf_parser import PDFParser, parse_pdf_file, validate_pdf_file
from .epub_parser import EPUBParser, parse_epub_file, validate_epub_file
from .base_parser import BaseParser

__all__ = [
    "BaseParser",
    "TxtParser", "parse_txt_file", "validate_txt_file",
    "FB2Parser", "parse_fb2_file", "validate_fb2_file", 
    "PDFParser", "parse_pdf_file", "validate_pdf_file",
    "EPUBParser", "parse_epub_file", "validate_epub_file"
]
