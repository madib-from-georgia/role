"""
Middleware для оптимизации производительности.
"""

import time
import asyncio
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import psutil
import uuid

from app.utils.logging_config import LoggingConfig


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware для мониторинга производительности."""
    
    def __init__(self, app, max_request_time: float = 30.0):
        """
        Args:
            app: FastAPI приложение
            max_request_time: Максимальное время выполнения запроса в секундах
        """
        super().__init__(app)
        self.max_request_time = max_request_time
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с мониторингом производительности."""
        
        # Генерируем уникальный ID запроса
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Засекаем время начала
        start_time = time.time()
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = process.cpu_percent()
        
        try:
            # Создаем task с таймаутом
            response_task = asyncio.create_task(call_next(request))
            
            try:
                response = await asyncio.wait_for(response_task, timeout=self.max_request_time)
            except asyncio.TimeoutError:
                # Запрос превысил максимальное время выполнения
                LoggingConfig.get_api_logger().error(
                    f"Request timeout: {request.method} {request.url.path}",
                    request_id=request_id,
                    timeout=self.max_request_time
                )
                return JSONResponse(
                    status_code=408,
                    content={"error": "Request timeout", "request_id": request_id}
                )
            
            # Вычисляем метрики
            duration_ms = (time.time() - start_time) * 1000
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = end_memory - start_memory
            
            # Логируем метрики производительности
            if duration_ms > 1000:  # Больше 1 секунды
                LoggingConfig.get_api_logger().warning(
                    f"Slow request: {request.method} {request.url.path}",
                    duration_ms=duration_ms,
                    memory_usage_mb=memory_diff,
                    request_id=request_id
                )
            
            # Добавляем заголовки с метриками
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            response.headers["X-Memory-Usage"] = f"{memory_diff:.2f}MB"
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            LoggingConfig.get_api_logger().error(
                f"Request error: {request.method} {request.url.path}",
                error=str(e),
                duration_ms=duration_ms,
                request_id=request_id
            )
            raise


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware для кеширования ответов."""
    
    def __init__(self, app, cache_ttl: int = 300):  # 5 минут по умолчанию
        """
        Args:
            app: FastAPI приложение
            cache_ttl: Время жизни кеша в секундах
        """
        super().__init__(app)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = cache_ttl
        
    def _should_cache(self, request: Request) -> bool:
        """Определяет, нужно ли кешировать запрос."""
        # Кешируем только GET запросы
        if request.method != "GET":
            return False
            
        # Кешируем только определенные endpoints
        cacheable_paths = [
            "/api/checklists/",
            "/api/export/templates",
            "/api/export/formats",
            "/api/export/types"
        ]
        
        return any(request.url.path.startswith(path) for path in cacheable_paths)
    
    def _get_cache_key(self, request: Request) -> str:
        """Генерирует ключ кеша для запроса."""
        # Учитываем путь, query параметры и user_id
        user_id = getattr(request.state, 'user_id', 'anonymous')
        query_string = str(request.query_params)
        return f"{request.url.path}:{query_string}:user_{user_id}"
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Проверяет, актуален ли кеш."""
        if not cache_entry:
            return False
        
        current_time = time.time()
        return (current_time - cache_entry['timestamp']) < self.cache_ttl
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с кешированием."""
        
        if not self._should_cache(request):
            return await call_next(request)
        
        cache_key = self._get_cache_key(request)
        
        # Проверяем кеш
        cache_entry = self.cache.get(cache_key)
        if cache_entry and self._is_cache_valid(cache_entry):
            LoggingConfig.get_api_logger().info(
                f"Cache hit: {request.method} {request.url.path}",
                cache_key=cache_key
            )
            
            # Возвращаем закешированный ответ
            response = JSONResponse(
                content=cache_entry['content'],
                status_code=cache_entry['status_code']
            )
            response.headers["X-Cache"] = "HIT"
            return response
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Кешируем только успешные JSON ответы
        if (response.status_code == 200 and 
            response.headers.get("content-type", "").startswith("application/json")):
            try:
                # Читаем содержимое ответа безопасно
                if hasattr(response, 'body'):
                    response_body = response.body
                else:
                    # Собираем body из iterator
                    response_body = b""
                    body_parts = []
                    async for chunk in response.body_iterator:
                        body_parts.append(chunk)
                    response_body = b"".join(body_parts)
                
                # Декодируем JSON (только для текстовых ответов)
                import json
                try:
                    content = json.loads(response_body.decode('utf-8'))
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    # Если не удается декодировать как JSON, пропускаем кеширование
                    LoggingConfig.get_api_logger().debug(
                        f"Skipping cache for non-JSON response: {str(e)}",
                        path=request.url.path
                    )
                    response.headers["X-Cache"] = "SKIP"
                    return response
                
                # Сохраняем в кеш
                self.cache[cache_key] = {
                    'content': content,
                    'status_code': response.status_code,
                    'timestamp': time.time()
                }
                
                LoggingConfig.get_api_logger().info(
                    f"Cache miss - cached: {request.method} {request.url.path}",
                    cache_key=cache_key
                )
                
                # Создаем новый ответ без копирования заголовков
                new_response = JSONResponse(
                    content=content,
                    status_code=response.status_code
                )
                new_response.headers["X-Cache"] = "MISS"
                return new_response
                
            except Exception as e:
                LoggingConfig.get_api_logger().warning(
                    f"Failed to cache response: {str(e)}",
                    cache_key=cache_key
                )
        
        # Добавляем заголовок без модификации ответа
        response.headers["X-Cache"] = "SKIP" 
        return response
    
    def clear_cache(self, pattern: str = None):
        """Очищает кеш по паттерну или полностью."""
        if pattern:
            keys_to_delete = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_delete:
                del self.cache[key]
        else:
            self.cache.clear()
        
        LoggingConfig.get_api_logger().info(
            f"Cache cleared",
            pattern=pattern or "all",
            cleared_items=len(keys_to_delete) if pattern else "all"
        )


class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware для сжатия ответов."""
    
    def __init__(self, app, min_size: int = 1024):
        """
        Args:
            app: FastAPI приложение
            min_size: Минимальный размер ответа для сжатия в байтах
        """
        super().__init__(app)
        self.min_size = min_size
    
    def _should_compress(self, response: Response, content_length: int) -> bool:
        """Определяет, нужно ли сжимать ответ."""
        # Сжимаем только если размер больше минимального
        if content_length < self.min_size:
            return False
        
        # Сжимаем только текстовые форматы
        content_type = response.headers.get("content-type", "")
        compressible_types = [
            "application/json",
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript"
        ]
        
        return any(ct in content_type for ct in compressible_types)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса со сжатием."""
        response = await call_next(request)
        
        # Проверяем поддержку сжатия клиентом
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response
        
        # Проверяем, нужно ли сжимать (упрощенная проверка)
        content_type = response.headers.get("content-type", "")
        if not any(ct in content_type for ct in ["application/json", "text/", "application/javascript"]):
            return response
        
        # Получаем размер ответа
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.min_size:
            return response
        
        try:
            import gzip
            
            # Безопасно читаем тело ответа
            if hasattr(response, 'body'):
                response_body = response.body
            else:
                response_body = b""
                body_parts = []
                async for chunk in response.body_iterator:
                    body_parts.append(chunk)
                response_body = b"".join(body_parts)
            
            # Проверяем размер после чтения
            if len(response_body) < self.min_size:
                return response
            
            # Сжимаем
            compressed_body = gzip.compress(response_body)
            
            # Создаем новый ответ со сжатым содержимым
            from fastapi.responses import Response as FastAPIResponse
            new_response = FastAPIResponse(
                content=compressed_body,
                status_code=response.status_code,
                media_type=response.media_type
            )
            
            # Устанавливаем заголовки сжатия
            new_response.headers["content-encoding"] = "gzip"
            new_response.headers["content-length"] = str(len(compressed_body))
            new_response.headers["vary"] = "Accept-Encoding"
            
            # Копируем остальные заголовки (кроме content-length)
            for key, value in response.headers.items():
                if key.lower() not in ["content-length", "content-encoding"]:
                    new_response.headers[key] = value
            
            return new_response
            
        except Exception as e:
            LoggingConfig.get_api_logger().warning(
                f"Compression failed: {str(e)}"
            )
            return response


# Глобальные экземпляры middleware
performance_middleware = None
cache_middleware = None
compression_middleware = None

def get_performance_middleware():
    """Получить экземпляр PerformanceMiddleware."""
    global performance_middleware
    if performance_middleware is None:
        performance_middleware = PerformanceMiddleware
    return performance_middleware

def get_cache_middleware():
    """Получить экземпляр CacheMiddleware."""
    global cache_middleware
    if cache_middleware is None:
        cache_middleware = CacheMiddleware
    return cache_middleware

def get_compression_middleware():
    """Получить экземпляр CompressionMiddleware.""" 
    global compression_middleware
    if compression_middleware is None:
        compression_middleware = CompressionMiddleware
    return compression_middleware
