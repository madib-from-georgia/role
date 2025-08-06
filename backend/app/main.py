"""
Главный файл FastAPI приложения для анализа персонажей.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.database.connection import init_db, close_db
from app.middleware.auth_middleware import AuthMiddleware, SecurityMiddleware, LoggingMiddleware
from app.routers import auth, projects, texts, characters, checklists
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Создание FastAPI приложения
app = FastAPI(
    title="Анализ Персонажей API",
    description="API для детального анализа персонажей художественных произведений",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавление кастомных middleware (порядок важен!)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityMiddleware, rate_limit_requests=100, rate_limit_window=60)

# Добавляем AuthMiddleware только если авторизация включена
if settings.auth_enabled:
    app.add_middleware(AuthMiddleware)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(texts.router, prefix="/api/texts", tags=["texts"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(checklists.router, prefix="/api/checklists", tags=["checklists"])


@app.get("/")
async def root():
    """Корневой endpoint."""
    return {"message": "Анализ Персонажей API v1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик исключений."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
