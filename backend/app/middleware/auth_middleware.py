"""
Middleware для авторизации и безопасности.
"""

import time
from typing import Optional, Dict, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db_session
from app.services.auth import auth_service
from app.config.settings import settings


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware для безопасности и rate limiting."""
    
    def __init__(self, app, rate_limit_requests: int = 100, rate_limit_window: int = 60):
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.request_counts: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: StarletteRequest, call_next) -> StarletteResponse:
        """Обработка запроса через middleware."""
        start_time = time.time()
        
        # Rate limiting
        client_ip = self._get_client_ip(request)
        if not self._check_rate_limit(client_ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Слишком много запросов. Попробуйте позже."}
            )
        
        # Добавляем заголовки безопасности
        response = await call_next(request)
        
        # Время обработки
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Заголовки безопасности
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    
    def _get_client_ip(self, request: StarletteRequest) -> str:
        """Получение IP адреса клиента."""
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Проверка rate limiting."""
        current_time = time.time()
        
        # Очищаем старые записи
        if client_ip in self.request_counts:
            self.request_counts[client_ip]["requests"] = [
                req_time for req_time in self.request_counts[client_ip]["requests"]
                if current_time - req_time < self.rate_limit_window
            ]
        else:
            self.request_counts[client_ip] = {"requests": []}
        
        # Проверяем лимит
        if len(self.request_counts[client_ip]["requests"]) >= self.rate_limit_requests:
            return False
        
        # Добавляем текущий запрос
        self.request_counts[client_ip]["requests"].append(current_time)
        return True


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware для автоматической проверки авторизации на защищенных маршрутах."""
    
    def __init__(self, app):
        super().__init__(app)
        # Пути, которые не требуют авторизации
        self.public_paths = {
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/api/auth/register",
            "/api/auth/login",
            "/api/auth/refresh",
            "/health",
            "/"
        }
    
    async def dispatch(self, request: StarletteRequest, call_next) -> StarletteResponse:
        """Обработка запроса через middleware."""
        path = request.url.path
        
        # Если авторизация отключена, пропускаем все запросы
        if not settings.auth_enabled:
            return await call_next(request)
        
        # Пропускаем публичные пути
        if self._is_public_path(path):
            return await call_next(request)
        
        # Для защищенных путей проверяем авторизацию
        if path.startswith("/api/"):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Требуется авторизация"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            token = auth_header.split(" ")[1]
            
            # Проверяем токен
            with get_db_session() as db:
                user = auth_service.get_current_user(db, token)
                if not user:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Неверный токен авторизации"},
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                
                # Добавляем пользователя в state для использования в endpoints
                request.state.current_user = user
        
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """Проверка, является ли путь публичным."""
        # Точное совпадение
        if path in self.public_paths:
            return True
        
        # Проверяем паттерны
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True
        
        return False


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов."""
    
    async def dispatch(self, request: StarletteRequest, call_next) -> StarletteResponse:
        """Логирование запросов."""
        start_time = time.time()
        
        # Логируем входящий запрос
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        
        print(f"🔍 {method} {url} from {client_ip}")
        
        # Обрабатываем запрос
        response = await call_next(request)
        
        # Логируем результат
        process_time = time.time() - start_time
        status_code = response.status_code
        
        print(f"✅ {method} {url} -> {status_code} ({process_time:.3f}s)")
        
        return response
