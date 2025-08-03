"""
Тесты для специализированных парсеров файлов.
"""

import pytest
import tempfile
import os
from pathlib import Path

from app.parsers.txt_parser import TxtParser, parse_txt_file, validate_txt_file
from app.parsers.fb2_parser import FB2Parser, parse_fb2_file, validate_fb2_file
from app.parsers.pdf_parser import PDFParser, parse_pdf_file, validate_pdf_file
from app.parsers.epub_parser import EPUBParser, parse_epub_file, validate_epub_file


class TestTxtParser:
    """Unit тесты для TxtParser."""
    
    def test_txt_parser_init(self):
        """Тест инициализации TxtParser."""
        parser = TxtParser()
        
        assert parser.supported_extensions == ['.txt']
        assert parser.max_file_size == 10 * 1024 * 1024
        assert 'utf-8' in parser.supported_encodings
        assert 'windows-1251' in parser.supported_encodings
    
    def test_clean_text(self):
        """Тест очистки текста."""
        parser = TxtParser()
        
        # Обычный текст с проблемами форматирования
        dirty_text = "  Привет   мир!  \n\n\nЭто   тест.  \r\n  Конец.  "
        clean = parser.clean_text(dirty_text)
        assert clean == "Привет мир!\n\nЭто тест.\nКонец."
        
        # Пустой текст
        assert parser.clean_text("") == ""
        assert parser.clean_text(None) == ""
        
        # Только пробелы
        assert parser.clean_text("   \n\n  ") == ""
    
    def test_parse_txt_file(self):
        """Тест парсинга TXT файла."""
        parser = TxtParser()
        
        # Создаем временный TXT файл
        test_content = "Заголовок произведения\nАвтор: Иван Тестов\n\nЭто тестовый текст для анализа."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', encoding='utf-8', delete=False) as f:
            f.write(test_content)
            temp_path = f.name
        
        try:
            result = parser.parse_file(temp_path)
            
            assert 'content' in result
            assert 'metadata' in result
            assert result['content'] == test_content
            assert result['metadata']['encoding'] == 'utf-8'
            assert result['metadata']['format'] == 'txt'
            assert result['metadata']['line_count'] == 4
            assert 'word_count' in result['metadata']
            
            # Проверяем извлечение заголовка и автора
            assert 'title' in result['metadata']
            assert 'author' in result['metadata']
            assert result['metadata']['title'] == "Заголовок произведения"
            assert result['metadata']['author'] == "Иван Тестов"
            
        finally:
            os.unlink(temp_path)
    
    def test_validate_txt_file(self):
        """Тест валидации TXT файла."""
        parser = TxtParser()
        
        # Валидный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', encoding='utf-8', delete=False) as f:
            f.write("Тестовый контент")
            temp_path = f.name
        
        try:
            assert parser.validate_file(temp_path) is True
        finally:
            os.unlink(temp_path)
        
        # Несуществующий файл
        assert parser.validate_file("/несуществующий/файл.txt") is False
    
    def test_parse_txt_file_wrapper(self):
        """Тест функции-обертки для парсинга."""
        test_content = "Тест функции-обертки"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', encoding='utf-8', delete=False) as f:
            f.write(test_content)
            temp_path = f.name
        
        try:
            result = parse_txt_file(temp_path)
            assert result['content'] == test_content
            assert result['metadata']['format'] == 'txt'
        finally:
            os.unlink(temp_path)
    
    def test_validate_txt_file_wrapper(self):
        """Тест функции-обертки для валидации."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', encoding='utf-8', delete=False) as f:
            f.write("Тест валидации")
            temp_path = f.name
        
        try:
            assert validate_txt_file(temp_path) is True
        finally:
            os.unlink(temp_path)


class TestFB2Parser:
    """Unit тесты для FB2Parser."""
    
    def test_fb2_parser_init(self):
        """Тест инициализации FB2Parser."""
        parser = FB2Parser()
        
        assert parser.supported_extensions == ['.fb2']
        assert parser.max_file_size == 20 * 1024 * 1024
        assert 'fb' in parser.namespaces
        assert parser.namespaces['fb'] == 'http://www.gribuser.ru/xml/fictionbook/2.0'
    
    def test_clean_text(self):
        """Тест очистки текста."""
        parser = FB2Parser()
        
        dirty_text = "  Текст   с   проблемами  \n\n\n  форматирования.  "
        clean = parser.clean_text(dirty_text)
        assert clean == "Текст с проблемами\n\nформатирования."
    
    def test_parse_fb2_file(self):
        """Тест парсинга FB2 файла."""
        parser = FB2Parser()
        
        # Создаем простой FB2 файл
        fb2_content = '''<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
    <description>
        <title-info>
            <genre>sf</genre>
            <author>
                <first-name>Иван</first-name>
                <last-name>Тестов</last-name>
            </author>
            <book-title>Тестовая книга</book-title>
            <annotation>
                <p>Это тестовая аннотация</p>
            </annotation>
            <keywords>тест, книга</keywords>
            <date>2023</date>
            <lang>ru</lang>
        </title-info>
        <document-info>
            <author>
                <first-name>Программа</first-name>
                <last-name>Тест</last-name>
            </author>
            <program-used>Test Suite</program-used>
            <date value="2023-12-01">1 декабря 2023</date>
        </document-info>
    </description>
    <body>
        <section>
            <title>
                <p>Глава 1</p>
            </title>
            <p>Это первая строка тестового текста.</p>
            <p>Это вторая строка.</p>
        </section>
        <section>
            <title>
                <p>Глава 2</p>
            </title>
            <p>Содержимое второй главы.</p>
        </section>
    </body>
</FictionBook>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fb2', encoding='utf-8', delete=False) as f:
            f.write(fb2_content)
            temp_path = f.name
        
        try:
            result = parser.parse_file(temp_path)
            
            assert 'content' in result
            assert 'metadata' in result
            
            # Проверяем, что текст извлечен
            content = result['content']
            assert "Это первая строка тестового текста." in content
            assert "Это вторая строка." in content
            assert "Содержимое второй главы." in content
            
            # Проверяем метаданные
            metadata = result['metadata']
            assert metadata['format'] == 'fb2'
            assert 'fb2_info' in metadata
            
            fb2_info = metadata['fb2_info']
            assert fb2_info['title'] == 'Тестовая книга'
            assert 'Иван Тестов' in fb2_info['authors']
            assert ['sf'] == fb2_info['genres']
            assert fb2_info['annotation'].strip() == 'Это тестовая аннотация'
            assert fb2_info['keywords'] == 'тест, книга'
            assert fb2_info['date'] == '2023'
            assert fb2_info['language'] == 'ru'
            assert fb2_info['program_used'] == 'Test Suite'
            assert fb2_info['document_date'] == '2023-12-01'
            
        finally:
            os.unlink(temp_path)
    
    def test_validate_fb2_file(self):
        """Тест валидации FB2 файла."""
        parser = FB2Parser()
        
        # Валидный FB2 файл
        valid_fb2 = '''<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
    <description>
        <title-info>
            <book-title>Тест</book-title>
        </title-info>
    </description>
    <body>
        <section>
            <p>Тест</p>
        </section>
    </body>
</FictionBook>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fb2', encoding='utf-8', delete=False) as f:
            f.write(valid_fb2)
            temp_path = f.name
        
        try:
            assert parser.validate_file(temp_path) is True
        finally:
            os.unlink(temp_path)
        
        # Невалидный XML
        invalid_xml = '''<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
    <description>
        <unclosed_tag>
    </description>
</FictionBook>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fb2', encoding='utf-8', delete=False) as f:
            f.write(invalid_xml)
            temp_path = f.name
        
        try:
            assert parser.validate_file(temp_path) is False
        finally:
            os.unlink(temp_path)


class TestPDFParser:
    """Unit тесты для PDFParser."""
    
    def test_pdf_parser_init(self):
        """Тест инициализации PDFParser."""
        parser = PDFParser()
        
        assert parser.supported_extensions == ['.pdf']
        assert parser.max_file_size == 50 * 1024 * 1024
    
    def test_clean_text(self):
        """Тест очистки текста."""
        parser = PDFParser()
        
        # Текст с артефактами PDF
        dirty_text = "Заголовок\n\n1\n\nСтр. 1\n\nОсновной текст\n\n2\n\npage 2\n\nЕще текст"
        clean = parser.clean_text(dirty_text)
        
        # Проверяем, что номера страниц удалены
        assert "1" not in clean or clean.count("1") == 0
        assert "стр." not in clean.lower()
        assert "page" not in clean.lower()
        assert "Основной текст" in clean
        assert "Еще текст" in clean
    
    def test_remove_pdf_artifacts(self):
        """Тест удаления артефактов PDF."""
        parser = PDFParser()
        
        text_with_artifacts = "Текст\n1\nСтр. 5\npage 10\nГлава 1\nЕще текст"
        clean = parser._remove_pdf_artifacts(text_with_artifacts)
        
        assert "1" not in clean
        assert "Стр. 5" not in clean
        assert "page 10" not in clean
        assert "Текст" in clean
        assert "Еще текст" in clean


class TestEPUBParser:
    """Unit тесты для EPUBParser."""
    
    def test_epub_parser_init(self):
        """Тест инициализации EPUBParser."""
        parser = EPUBParser()
        
        assert parser.supported_extensions == ['.epub']
        assert parser.max_file_size == 100 * 1024 * 1024
    
    def test_extract_metadata_from_opf(self):
        """Тест извлечения метаданных из OPF."""
        parser = EPUBParser()
        
        opf_content = '''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>Тестовая книга EPUB</dc:title>
        <dc:creator>Иван Тестов</dc:creator>
        <dc:creator>Петр Второй</dc:creator>
        <dc:language>ru</dc:language>
        <dc:publisher>Тестовое издательство</dc:publisher>
        <dc:date>2023-12-01</dc:date>
        <dc:description>Это тестовое описание книги</dc:description>
        <dc:identifier scheme="ISBN">978-0-123456-78-9</dc:identifier>
        <dc:rights>Все права защищены</dc:rights>
    </metadata>
</package>'''
        
        metadata = parser.extract_metadata_from_opf(opf_content)
        
        assert metadata['title'] == 'Тестовая книга EPUB'
        assert 'Иван Тестов' in metadata['authors']
        assert 'Петр Второй' in metadata['authors']
        assert metadata['language'] == 'ru'
        assert metadata['publisher'] == 'Тестовое издательство'
        assert metadata['date'] == '2023-12-01'
        assert metadata['description'] == 'Это тестовое описание книги'
        assert metadata['rights'] == 'Все права защищены'
        assert 'identifiers' in metadata
    
    def test_extract_text_from_html(self):
        """Тест извлечения текста из HTML."""
        parser = EPUBParser()
        
        html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Глава 1</title>
    <style>body { font-family: Arial; }</style>
    <script>console.log("test");</script>
</head>
<body>
    <h1>Заголовок главы</h1>
    <p>Это первый параграф текста.</p>
    <p>Это второй параграф текста.</p>
    <div>Текст в div блоке.</div>
</body>
</html>'''
        
        text = parser.extract_text_from_html(html_content)
        
        assert "Заголовок главы" in text
        assert "Это первый параграф текста." in text
        assert "Это второй параграф текста." in text
        assert "Текст в div блоке." in text
        # Проверяем, что теги удалены
        assert "<p>" not in text
        assert "<div>" not in text
        assert "console.log" not in text


class TestParserWrappers:
    """Тесты для функций-оберток парсеров."""
    
    def test_all_parsers_have_wrappers(self):
        """Проверяем, что все парсеры имеют функции-обертки."""
        # TXT
        assert callable(parse_txt_file)
        assert callable(validate_txt_file)
        
        # FB2
        assert callable(parse_fb2_file)
        assert callable(validate_fb2_file)
        
        # PDF
        assert callable(parse_pdf_file)
        assert callable(validate_pdf_file)
        
        # EPUB
        assert callable(parse_epub_file)
        assert callable(validate_epub_file)
    
    def test_wrappers_call_parser_methods(self):
        """Проверяем, что функции-обертки корректно вызывают методы парсеров."""
        # Создаем простой TXT файл для тестирования
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', encoding='utf-8', delete=False) as f:
            f.write("Тест обертки")
            temp_path = f.name
        
        try:
            # Тестируем TXT обертки
            result = parse_txt_file(temp_path)
            assert isinstance(result, dict)
            assert 'content' in result
            assert 'metadata' in result
            
            is_valid = validate_txt_file(temp_path)
            assert isinstance(is_valid, bool)
            assert is_valid is True
            
        finally:
            os.unlink(temp_path)
