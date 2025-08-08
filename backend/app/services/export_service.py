"""
Сервис для экспорта данных персонажей в различных форматах.
"""

import io
import os
import time
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime
from pathlib import Path

# PDF генерация
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# DOCX генерация
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement, qn

# HTML to PDF (опциональное)
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    weasyprint = None

from jinja2 import Template, Environment, FileSystemLoader

from app.database.models.character import Character
from app.database.models.checklist import ChecklistResponse
from app.schemas.checklist import ChecklistWithResponses
from app.config.settings import settings
from app.utils.error_handlers import ExportError, ErrorHandler, ErrorCode
from app.utils.logging_config import LoggingConfig


class ExportService:
    """Сервис для экспорта данных персонажей в PDF и DOCX форматы."""
    
    def __init__(self):
        """Инициализация сервиса экспорта."""
        self.template_dir = Path(__file__).parent.parent / "templates" / "export"
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Настройка Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
        
        # Проверяем доступность WeasyPrint
        if not WEASYPRINT_AVAILABLE:
            LoggingConfig.get_export_logger().warning(
                "WeasyPrint not available - HTML to PDF conversion disabled"
            )
        
        # Попытка зарегистрировать шрифт поддерживающий кириллицу для ReportLab
        try:
            font_path = self._find_cyrillic_font()
            if font_path:
                pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                self.default_font = 'DejaVuSans'
            else:
                self.default_font = 'Helvetica'
        except Exception:
            self.default_font = 'Helvetica'
    
    def _find_cyrillic_font(self) -> Optional[str]:
        """Поиск шрифта с поддержкой кириллицы."""
        # Общие пути к шрифтам в разных ОС
        font_paths = [
            '/System/Library/Fonts/Helvetica.ttc',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Ubuntu
            'C:\\Windows\\Fonts\\arial.ttf',  # Windows
            '/usr/share/fonts/TTF/DejaVuSans.ttf',  # Arch Linux
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return path
        return None
    
    async def export_character_pdf(
        self, 
        character: Character, 
        checklists: list[ChecklistWithResponses],
        format_type: str = "detailed",
        user_id: Optional[int] = None
    ) -> bytes:
        """
        Экспорт персонажа в PDF формат.
        
        Args:
            character: Модель персонажа
            checklists: Список чеклистов с ответами
            format_type: Тип отчета ('detailed', 'summary', 'compact')
            user_id: ID пользователя для логирования
            
        Returns:
            PDF файл в виде байтов
        """
        start_time = time.time()
        
        try:
            buffer = io.BytesIO()
            
            # Создание PDF документа
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Стили
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=styles['Heading1'],
                fontName=self.default_font,
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Центр
            ))
            
            styles.add(ParagraphStyle(
                name='CustomHeading',
                parent=styles['Heading2'],
                fontName=self.default_font,
                fontSize=16,
                spaceAfter=12
            ))
            
            styles.add(ParagraphStyle(
                name='CustomNormal',
                parent=styles['Normal'],
                fontName=self.default_font,
                fontSize=12,
                spaceAfter=6
            ))
            
            styles.add(ParagraphStyle(
                name='CustomBold',
                parent=styles['Normal'],
                fontName=self.default_font,
                fontSize=12,
                spaceAfter=4,
                textColor=colors.black
            ))
            
            # Контент документа
            story = []
            
            # Заголовок
            title = f"Анализ персонажа: {character.name}"
            story.append(Paragraph(title, styles['CustomTitle']))
            story.append(Spacer(1, 12))
            
            # Базовая информация о персонаже
            story.append(Paragraph("Базовая информация", styles['CustomHeading']))
            
            char_info = [
                ["Имя:", character.name],
                ["Важность:", f"{character.importance_score:.2f}" if character.importance_score else "Не определена"],
                ["Дата анализа:", datetime.now().strftime("%d.%m.%Y %H:%M")],
            ]
            
            if character.aliases:
                char_info.append(["Псевдонимы:", ", ".join(character.aliases)])
            
            # Таблица с информацией
            char_table = Table(char_info, colWidths=[2*inch, 4*inch])
            char_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(char_table)
            story.append(Spacer(1, 20))
            
            # Чеклисты
            if format_type == "detailed":
                story.extend(self._add_detailed_checklists_to_pdf(checklists, styles))
            elif format_type == "summary":
                story.extend(self._add_summary_checklists_to_pdf(checklists, styles))
            else:  # compact
                story.extend(self._add_compact_checklists_to_pdf(checklists, styles))
            
            # Генерация PDF
            doc.build(story)
            buffer.seek(0)
            
            duration_ms = (time.time() - start_time) * 1000
            file_size = len(buffer.getvalue())
            
            LoggingConfig.log_export_operation(
                operation="pdf_export",
                character_id=character.id,
                format_type=format_type,
                export_type="pdf",
                user_id=user_id,
                duration_ms=duration_ms,
                file_size=file_size,
                success=True
            )
            
            return buffer.getvalue()
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            LoggingConfig.log_export_operation(
                operation="pdf_export",
                character_id=character.id,
                format_type=format_type,
                export_type="pdf",
                user_id=user_id,
                duration_ms=duration_ms,
                success=False,
                error=str(e)
            )
            
            if "font" in str(e).lower():
                raise ExportError(
                    "Ошибка настройки шрифтов PDF",
                    details=f"Проблема с шрифтами: {str(e)}"
                )
            elif "reportlab" in str(e).lower():
                raise ExportError(
                    "Ошибка генерации PDF документа",
                    details=f"ReportLab ошибка: {str(e)}"
                )
            else:
                raise ExportError(
                    "Неизвестная ошибка при создании PDF",
                    details=str(e)
                )
    
    def _add_detailed_checklists_to_pdf(self, checklists: list, styles) -> list:
        """Добавить детальные чеклисты в PDF."""
        story = []
        
        for checklist in checklists:
            story.append(Paragraph(f"Чеклист: {checklist.title}", styles['CustomHeading']))
            
            if checklist.description:
                story.append(Paragraph(checklist.description, styles['CustomNormal']))
                story.append(Spacer(1, 6))
            
            # Проходим по структуре чеклиста напрямую
            for section in checklist.sections:
                if not section.subsections:
                    continue
                    
                story.append(Paragraph(f"📝 {section.title}", styles['CustomHeading']))
                
                for subsection in section.subsections:
                    for group in subsection.question_groups:
                        for question in group.questions:
                            if question.current_response and question.current_response.answer:
                                story.append(Paragraph(f"• {question.text}", styles['CustomNormal']))
                                story.append(Paragraph(question.current_response.answer, styles['CustomNormal']))
                                story.append(Spacer(1, 4))
                
                story.append(Spacer(1, 8))
            
            story.append(Spacer(1, 20))
        
        return story
    
    def _add_summary_checklists_to_pdf(self, checklists: list, styles) -> list:
        """Добавить краткие чеклисты в PDF."""
        story = []
        
        story.append(Paragraph("Краткий обзор чеклистов", styles['CustomHeading']))
        
        for checklist in checklists:
            # Подсчитываем общее количество вопросов и ответов
            total_questions = 0
            answered_questions = 0
            
            for section in checklist.sections:
                for subsection in section.subsections:
                    for group in subsection.question_groups:
                        for question in group.questions:
                            total_questions += 1
                            if question.current_response and question.current_response.answer:
                                answered_questions += 1
            
            completion_rate = (answered_questions / total_questions * 100) if total_questions > 0 else 0
            
            summary_data = [
                [checklist.title, f"{answered_questions}/{total_questions}", f"{completion_rate:.1f}%"]
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 1*inch, 1*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 6))
        
        return story
    
    def _add_compact_checklists_to_pdf(self, checklists: list, styles) -> list:
        """Добавить компактные чеклисты в PDF."""
        story = []
        
        story.append(Paragraph("Компактный отчет", styles['CustomHeading']))
        
        total_answered = 0
        total_questions = 0
        
        for checklist in checklists:
            # Подсчитываем вопросы из структуры checklist
            questions_count = 0
            answered_count = 0
            for section in checklist.sections:
                for subsection in section.subsections:
                    for group in subsection.question_groups:
                        for question in group.questions:
                            questions_count += 1
                            if question.current_response and question.current_response.answer:
                                answered_count += 1
            total_questions += questions_count
            total_answered += answered_count
        
        overall_completion = (total_answered / total_questions * 100) if total_questions > 0 else 0
        
        story.append(Paragraph(f"Общая статистика: {total_answered}/{total_questions} вопросов ({overall_completion:.1f}%)", styles['CustomNormal']))
        story.append(Spacer(1, 12))
        
        return story
    
    async def export_character_docx(
        self, 
        character: Character, 
        checklists: list[ChecklistWithResponses],
        format_type: str = "detailed",
        user_id: Optional[int] = None
    ) -> bytes:
        """
        Экспорт персонажа в DOCX формат.
        
        Args:
            character: Модель персонажа
            checklists: Список чеклистов с ответами
            format_type: Тип отчета ('detailed', 'summary', 'compact')
            user_id: ID пользователя для логирования
            
        Returns:
            DOCX файл в виде байтов
        """
        start_time = time.time()
        
        try:
            # Создание документа
            doc = Document()
            
            # Заголовок
            title = doc.add_heading(f'Анализ персонажа: {character.name}', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Базовая информация
            doc.add_heading('Базовая информация', level=1)
            
            info_table = doc.add_table(rows=3, cols=2)
            info_table.style = 'Table Grid'
            
            info_table.cell(0, 0).text = 'Имя:'
            info_table.cell(0, 1).text = character.name
            
            info_table.cell(1, 0).text = 'Важность:'
            info_table.cell(1, 1).text = f"{character.importance_score:.2f}" if character.importance_score else "Не определена"
            
            info_table.cell(2, 0).text = 'Дата анализа:'
            info_table.cell(2, 1).text = datetime.now().strftime("%d.%m.%Y %H:%M")
            
            if character.aliases:
                row = info_table.add_row()
                row.cells[0].text = 'Псевдонимы:'
                row.cells[1].text = ', '.join(character.aliases)
            
            # Добавляем чеклисты в зависимости от формата
            if format_type == "detailed":
                self._add_detailed_checklists_to_docx(doc, checklists)
            elif format_type == "summary":
                self._add_summary_checklists_to_docx(doc, checklists)
            else:  # compact
                self._add_compact_checklists_to_docx(doc, checklists)
            
            # Сохранение в байты
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            duration_ms = (time.time() - start_time) * 1000
            file_size = len(buffer.getvalue())
            
            LoggingConfig.log_export_operation(
                operation="docx_export",
                character_id=character.id,
                format_type=format_type,
                export_type="docx",
                user_id=user_id,
                duration_ms=duration_ms,
                file_size=file_size,
                success=True
            )
            
            return buffer.getvalue()
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            LoggingConfig.log_export_operation(
                operation="docx_export",
                character_id=character.id,
                format_type=format_type,
                export_type="docx",
                user_id=user_id,
                duration_ms=duration_ms,
                success=False,
                error=str(e)
            )
            
            if "docx" in str(e).lower() or "document" in str(e).lower():
                raise ExportError(
                    "Ошибка создания DOCX документа",
                    details=f"python-docx ошибка: {str(e)}"
                )
            else:
                raise ExportError(
                    "Неизвестная ошибка при создании DOCX",
                    details=str(e)
                )
    
    def _add_detailed_checklists_to_docx(self, doc: Document, checklists: list):
        """Добавить детальные чеклисты в DOCX."""
        for checklist in checklists:
            doc.add_heading(f'Чеклист: {checklist.title}', level=1)
            
            if checklist.description:
                doc.add_paragraph(checklist.description)
            
            # Проходим по структуре чеклиста для DOCX
            for section in checklist.sections:
                if not section.subsections:
                    continue
                    
                doc.add_heading(section.title, level=2)
                
                for subsection in section.subsections:
                    for group in subsection.question_groups:
                        for question in group.questions:
                            if question.current_response and question.current_response.answer:
                                # Вопрос
                                question_p = doc.add_paragraph()
                                question_p.add_run('Вопрос: ').bold = True
                                question_p.add_run(question.text)
                                
                                # Ответ
                                answer_p = doc.add_paragraph()
                                answer_p.add_run('Ответ: ').bold = True
                                answer_p.add_run(question.current_response.answer)
                    
                    # Источник и уверенность (только если есть response)
                    if question.current_response and hasattr(question.current_response, 'source_type'):
                        source_text = {
                            "FOUND_IN_TEXT": "Найдено в тексте",
                            "LOGICALLY_DERIVED": "Логически выведено",
                            "IMAGINED": "Придумано"
                        }.get(question.current_response.source_type.value if question.current_response.source_type else "UNKNOWN", "Неизвестно")
                        
                        source_p = doc.add_paragraph()
                        source_p.add_run('Источник: ').bold = True
                        source_p.add_run(source_text)
                    
                    # Note: ChecklistResponse doesn't have confidence_score field
                    # if question.current_response.confidence_score:
                    #     confidence_p = doc.add_paragraph()
                    #     confidence_p.add_run('Уверенность: ').bold = True
                    #     confidence_p.add_run(f"{question.current_response.confidence_score:.2f}")
                    
                    doc.add_paragraph("")  # Пустая строка для разделения
    
    def _add_summary_checklists_to_docx(self, doc: Document, checklists: list):
        """Добавить краткие чеклисты в DOCX."""
        doc.add_heading('Краткий обзор чеклистов', level=1)
        
        summary_table = doc.add_table(rows=1, cols=3)
        summary_table.style = 'Table Grid'
        
        # Заголовки
        hdr_cells = summary_table.rows[0].cells
        hdr_cells[0].text = 'Чеклист'
        hdr_cells[1].text = 'Отвечено'
        hdr_cells[2].text = 'Процент'
        
        for checklist in checklists:
            row_cells = summary_table.add_row().cells
            # Подсчитываем вопросы из структуры checklist для DOCX summary
            total_questions = 0
            answered_questions = 0
            for section in checklist.sections:
                for subsection in section.subsections:
                    for group in subsection.question_groups:
                        for question in group.questions:
                            total_questions += 1
                            if question.current_response and question.current_response.answer:
                                answered_questions += 1
            completion_rate = (answered_questions / total_questions * 100) if total_questions > 0 else 0
            
            row_cells[0].text = checklist.title
            row_cells[1].text = f"{answered_questions}/{total_questions}"
            row_cells[2].text = f"{completion_rate:.1f}%"
    
    def _add_compact_checklists_to_docx(self, doc: Document, checklists: list):
        """Добавить компактные чеклисты в DOCX."""
        doc.add_heading('Компактный отчет', level=1)
        
        total_answered = 0
        total_questions = 0
        
        for checklist in checklists:
            # Подсчитываем вопросы из структуры checklist
            questions_count = 0
            answered_count = 0
            for section in checklist.sections:
                for subsection in section.subsections:
                    for group in subsection.question_groups:
                        for question in group.questions:
                            questions_count += 1
                            if question.current_response and question.current_response.answer:
                                answered_count += 1
            total_questions += questions_count
            total_answered += answered_count
        
        overall_completion = (total_answered / total_questions * 100) if total_questions > 0 else 0
        
        doc.add_paragraph(f"Общая статистика: {total_answered}/{total_questions} вопросов ({overall_completion:.1f}%)")


# Создание экземпляра сервиса
export_service = ExportService()
