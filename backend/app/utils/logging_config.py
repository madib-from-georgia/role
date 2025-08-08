"""
Конфигурация логирования для приложения.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from loguru import logger
from app.config.settings import settings


class LoggingConfig:
    """Конфигурация логирования."""
    
    @staticmethod
    def setup_logging():
        """Настройка системы логирования."""
        
        # Удаляем стандартный обработчик loguru
        logger.remove()
        
        # Создаем директорию для логов
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Формат логов
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # Консольное логирование
        console_level = "DEBUG" if settings.debug else "INFO"
        logger.add(
            sys.stdout,
            format=log_format,
            level=console_level,
            colorize=True,
            backtrace=settings.debug,
            diagnose=settings.debug
        )
        
        # Файловое логирование - общий лог
        logger.add(
            log_dir / "app.log",
            format=log_format,
            level="INFO",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Файловое логирование - только ошибки
        logger.add(
            log_dir / "errors.log",
            format=log_format,
            level="ERROR",
            rotation="10 MB",
            retention="90 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Файловое логирование - API запросы
        logger.add(
            log_dir / "api.log",
            format=log_format,
            level="INFO",
            rotation="50 MB",
            retention="7 days",
            compression="zip",
            filter=lambda record: "api" in record["extra"],
            backtrace=False,
            diagnose=False
        )
        
        # Файловое логирование - экспорт
        logger.add(
            log_dir / "export.log",
            format=log_format,
            level="INFO",
            rotation="20 MB",
            retention="30 days",
            compression="zip",
            filter=lambda record: "export" in record["extra"],
            backtrace=True,
            diagnose=True
        )
        
        # Файловое логирование - NLP операции
        logger.add(
            log_dir / "nlp.log",
            format=log_format,
            level="INFO",
            rotation="30 MB",
            retention="14 days",
            compression="zip",
            filter=lambda record: "nlp" in record["extra"],
            backtrace=True,
            diagnose=True
        )
        
        logger.info("Logging system initialized")
    
    @staticmethod
    def get_api_logger():
        """Получить логгер для API операций."""
        return logger.bind(api=True)
    
    @staticmethod
    def get_export_logger():
        """Получить логгер для операций экспорта."""
        return logger.bind(export=True)
    
    @staticmethod
    def get_nlp_logger():
        """Получить логгер для NLP операций."""
        return logger.bind(nlp=True)
    
    @staticmethod
    def log_api_request(
        method: str,
        url: str,
        user_id: int = None,
        request_id: str = None,
        duration_ms: float = None,
        status_code: int = None,
        **extra_data
    ):
        """Логирование API запроса."""
        api_logger = LoggingConfig.get_api_logger()
        
        log_data = {
            "method": method,
            "url": url,
            "user_id": user_id,
            "request_id": request_id,
            "duration_ms": duration_ms,
            "status_code": status_code,
            **extra_data
        }
        
        message = f"{method} {url}"
        if duration_ms:
            message += f" ({duration_ms:.2f}ms)"
        if status_code:
            message += f" -> {status_code}"
        
        if status_code and status_code >= 400:
            api_logger.error(message, **log_data)
        else:
            api_logger.info(message, **log_data)
    
    @staticmethod
    def log_export_operation(
        operation: str,
        character_id: int,
        format_type: str,
        export_type: str,
        user_id: int = None,
        duration_ms: float = None,
        file_size: int = None,
        success: bool = True,
        error: str = None
    ):
        """Логирование операции экспорта."""
        export_logger = LoggingConfig.get_export_logger()
        
        log_data = {
            "operation": operation,
            "character_id": character_id,
            "format": format_type,
            "export_type": export_type,
            "user_id": user_id,
            "duration_ms": duration_ms,
            "file_size": file_size,
            "success": success,
            "error": error
        }
        
        message = f"Export {operation}: character={character_id}, format={format_type}, type={export_type}"
        if duration_ms:
            message += f" ({duration_ms:.2f}ms)"
        if file_size:
            message += f", size={file_size} bytes"
        
        if success:
            export_logger.info(message, **log_data)
        else:
            export_logger.error(f"{message} - FAILED: {error}", **log_data)
    
    @staticmethod
    def log_nlp_operation(
        operation: str,
        text_id: int,
        characters_found: int = None,
        duration_ms: float = None,
        success: bool = True,
        error: str = None
    ):
        """Логирование NLP операции."""
        nlp_logger = LoggingConfig.get_nlp_logger()
        
        log_data = {
            "operation": operation,
            "text_id": text_id,
            "characters_found": characters_found,
            "duration_ms": duration_ms,
            "success": success,
            "error": error
        }
        
        message = f"NLP {operation}: text={text_id}"
        if characters_found is not None:
            message += f", found={characters_found} characters"
        if duration_ms:
            message += f" ({duration_ms:.2f}ms)"
        
        if success:
            nlp_logger.info(message, **log_data)
        else:
            nlp_logger.error(f"{message} - FAILED: {error}", **log_data)


# Инициализация логирования при импорте модуля
LoggingConfig.setup_logging()
