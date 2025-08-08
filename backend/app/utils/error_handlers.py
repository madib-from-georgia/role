"""
Централизованная система обработки ошибок.
"""

import traceback
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger


class ErrorCode(str, Enum):
    """Коды ошибок для категоризации."""
    # Общие ошибки
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    
    # Ошибки авторизации
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_TOKEN = "INVALID_TOKEN"
    
    # Ошибки данных
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    INVALID_DATA = "INVALID_DATA"
    
    # Ошибки файлов
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    FILE_CORRUPTED = "FILE_CORRUPTED"
    
    # Ошибки экспорта
    EXPORT_FAILED = "EXPORT_FAILED"
    TEMPLATE_ERROR = "TEMPLATE_ERROR"
    FONT_ERROR = "FONT_ERROR"
    
    # Ошибки базы данных
    DATABASE_ERROR = "DATABASE_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    
    # Ошибки NLP
    NLP_PROCESSING_ERROR = "NLP_PROCESSING_ERROR"
    TEXT_ANALYSIS_ERROR = "TEXT_ANALYSIS_ERROR"


@dataclass
class ErrorDetails:
    """Детальная информация об ошибке."""
    code: ErrorCode
    message: str
    details: Optional[str] = None
    timestamp: str = None
    request_id: Optional[str] = None
    user_id: Optional[int] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class ApplicationError(Exception):
    """Базовый класс для ошибок приложения."""
    
    def __init__(
        self, 
        code: ErrorCode, 
        message: str, 
        details: Optional[str] = None,
        http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.code = code
        self.message = message
        self.details = details
        self.http_status = http_status
        super().__init__(message)
    
    def to_error_details(self, request_id: Optional[str] = None, user_id: Optional[int] = None) -> ErrorDetails:
        """Преобразование в ErrorDetails."""
        return ErrorDetails(
            code=self.code,
            message=self.message,
            details=self.details,
            request_id=request_id,
            user_id=user_id
        )


class ValidationError(ApplicationError):
    """Ошибка валидации данных."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            http_status=status.HTTP_400_BAD_REQUEST
        )


class NotFoundError(ApplicationError):
    """Ошибка - ресурс не найден."""
    
    def __init__(self, resource: str, resource_id: Any = None):
        message = f"{resource} не найден"
        if resource_id:
            message += f" (ID: {resource_id})"
        
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=message,
            http_status=status.HTTP_404_NOT_FOUND
        )


class ForbiddenError(ApplicationError):
    """Ошибка доступа."""
    
    def __init__(self, message: str = "Нет доступа к ресурсу"):
        super().__init__(
            code=ErrorCode.FORBIDDEN,
            message=message,
            http_status=status.HTTP_403_FORBIDDEN
        )


class ExportError(ApplicationError):
    """Ошибка экспорта."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            code=ErrorCode.EXPORT_FAILED,
            message=f"Ошибка экспорта: {message}",
            details=details,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class FileProcessingError(ApplicationError):
    """Ошибка обработки файлов."""
    
    def __init__(self, message: str, file_type: Optional[str] = None):
        details = f"Тип файла: {file_type}" if file_type else None
        super().__init__(
            code=ErrorCode.FILE_CORRUPTED,
            message=f"Ошибка обработки файла: {message}",
            details=details,
            http_status=status.HTTP_400_BAD_REQUEST
        )


class ErrorHandler:
    """Обработчик ошибок."""
    
    @staticmethod
    def log_error(
        error: Exception, 
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        request_id: Optional[str] = None
    ):
        """Логирование ошибки с контекстом."""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "user_id": user_id,
            "request_id": request_id,
            "context": context or {}
        }
        
        if isinstance(error, ApplicationError):
            error_info["error_code"] = error.code.value
            error_info["http_status"] = error.http_status
            
        # Логируем с разным уровнем в зависимости от типа ошибки
        if isinstance(error, (ValidationError, NotFoundError, ForbiddenError)):
            logger.warning("Application error", **error_info)
        else:
            logger.error("Application error", **error_info)
            # Для системных ошибок добавляем трейсбек
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    @staticmethod
    def create_error_response(
        error: Exception,
        request_id: Optional[str] = None,
        user_id: Optional[int] = None,
        include_details: bool = False
    ) -> JSONResponse:
        """Создание стандартизированного ответа об ошибке."""
        
        if isinstance(error, ApplicationError):
            error_details = error.to_error_details(request_id, user_id)
            http_status = error.http_status
        else:
            # Неожиданная ошибка
            error_details = ErrorDetails(
                code=ErrorCode.INTERNAL_ERROR,
                message="Внутренняя ошибка сервера",
                details=str(error) if include_details else None,
                request_id=request_id,
                user_id=user_id
            )
            http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Логируем ошибку
        ErrorHandler.log_error(error, request_id=request_id, user_id=user_id)
        
        response_data = asdict(error_details)
        
        # В продакшене не показываем детали внутренних ошибок
        if not include_details and error_details.code == ErrorCode.INTERNAL_ERROR:
            response_data["details"] = None
        
        return JSONResponse(
            status_code=http_status,
            content={
                "error": response_data,
                "success": False
            }
        )
    
    @staticmethod
    def handle_validation_errors(errors: list) -> ValidationError:
        """Обработка ошибок валидации Pydantic."""
        if not errors:
            return ValidationError("Ошибка валидации")
        
        # Форматируем ошибки валидации
        formatted_errors = []
        for error in errors:
            field = " -> ".join(str(loc) for loc in error.get("loc", []))
            message = error.get("msg", "Неизвестная ошибка")
            formatted_errors.append(f"{field}: {message}")
        
        return ValidationError(
            message="Ошибки валидации данных",
            details="; ".join(formatted_errors)
        )


# Вспомогательные функции для создания часто используемых ошибок
def character_not_found(character_id: int) -> NotFoundError:
    """Ошибка - персонаж не найден."""
    return NotFoundError("Персонаж", character_id)


def project_not_found(project_id: int) -> NotFoundError:
    """Ошибка - проект не найден."""
    return NotFoundError("Проект", project_id)


def text_not_found(text_id: int) -> NotFoundError:
    """Ошибка - текст не найден.""" 
    return NotFoundError("Текст", text_id)


def access_denied(resource: str = "ресурсу") -> ForbiddenError:
    """Ошибка доступа."""
    return ForbiddenError(f"Нет доступа к {resource}")


def invalid_file_format(supported_formats: list = None) -> ValidationError:
    """Ошибка - неподдерживаемый формат файла."""
    message = "Неподдерживаемый формат файла"
    if supported_formats:
        message += f". Поддерживаемые форматы: {', '.join(supported_formats)}"
    return ValidationError(message)


def file_too_large(max_size_mb: int) -> ValidationError:
    """Ошибка - файл слишком большой."""
    return ValidationError(f"Размер файла превышает лимит в {max_size_mb} МБ")


# Декоратор для автоматической обработки ошибок
def handle_errors(include_details: bool = False):
    """Декоратор для автоматической обработки ошибок в endpoint'ах."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # HTTPException уже обработан FastAPI
                raise
            except ApplicationError as e:
                # Наши кастомные ошибки
                raise HTTPException(
                    status_code=e.http_status,
                    detail=e.message
                )
            except Exception as e:
                # Неожиданные ошибки
                ErrorHandler.log_error(e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Внутренняя ошибка сервера" if not include_details else str(e)
                )
        return wrapper
    return decorator
