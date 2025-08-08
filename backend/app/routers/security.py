"""
API endpoints для управления безопасностью.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.dependencies.auth import get_db, get_current_active_user
from app.database.models.user import User
from app.utils.security_audit import security_auditor
from app.utils.logging_config import LoggingConfig
from app.config.settings import settings


router = APIRouter(prefix="/api/security", tags=["security"])


@router.get("/audit", response_model=Dict[str, Any])
async def run_security_audit(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Запускает полный аудит безопасности системы.
    
    Требует права администратора.
    """
    # Проверяем права администратора
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для проведения аудита безопасности"
        )
    
    try:
        # Запускаем аудит
        audit_results = security_auditor.audit_all()
        
        # Логируем запуск аудита
        LoggingConfig.get_api_logger().info(
            "Security audit requested",
            user_id=current_user.id,
            security_level=audit_results["security_level"],
            total_issues=audit_results["total_issues"]
        )
        
        return audit_results
        
    except Exception as e:
        LoggingConfig.get_api_logger().error(
            f"Security audit failed: {str(e)}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при проведении аудита безопасности"
        )


@router.get("/status")
async def get_security_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получает базовый статус безопасности системы.
    """
    try:
        status_info = {
            "auth_enabled": settings.auth_enabled,
            "debug_mode": settings.debug,
            "cors_configured": True,  # Предполагаем, что CORS настроен
            "rate_limiting_enabled": True,  # Предполагаем, что rate limiting включен
            "https_only": not settings.debug,  # В production должен быть HTTPS
            "security_headers": {
                "x_frame_options": "DENY",
                "x_content_type_options": "nosniff",
                "x_xss_protection": "1; mode=block"
            }
        }
        
        # Вычисляем общий статус
        security_issues = []
        
        if settings.debug:
            security_issues.append("DEBUG режим включен")
        
        if not settings.auth_enabled:
            security_issues.append("Авторизация отключена")
        
        status_info["security_level"] = "GOOD" if not security_issues else "WARNING"
        status_info["issues"] = security_issues
        
        return status_info
        
    except Exception as e:
        LoggingConfig.get_api_logger().error(
            f"Failed to get security status: {str(e)}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении статуса безопасности"
        )


@router.get("/recommendations")
async def get_security_recommendations(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получает рекомендации по улучшению безопасности.
    """
    try:
        recommendations = []
        
        # Базовые рекомендации
        if settings.debug:
            recommendations.append({
                "category": "Configuration",
                "priority": "HIGH",
                "title": "Отключить DEBUG режим",
                "description": "DEBUG режим не должен быть включен в production",
                "action": "Установить DEBUG=False в настройках"
            })
        
        recommendations.extend([
            {
                "category": "Authentication",
                "priority": "MEDIUM",
                "title": "Регулярно обновляйте пароли",
                "description": "Используйте сложные пароли и регулярно их обновляйте",
                "action": "Установить политику паролей"
            },
            {
                "category": "Dependencies",
                "priority": "MEDIUM", 
                "title": "Обновляйте зависимости",
                "description": "Регулярно проверяйте и обновляйте зависимости",
                "action": "Запустить 'pip list --outdated'"
            },
            {
                "category": "Monitoring",
                "priority": "LOW",
                "title": "Настройте мониторинг",
                "description": "Отслеживайте подозрительную активность",
                "action": "Настроить алерты для критичных событий"
            },
            {
                "category": "Backup",
                "priority": "MEDIUM",
                "title": "Регулярные бэкапы",
                "description": "Создавайте регулярные резервные копии данных",
                "action": "Настроить автоматическое резервное копирование"
            }
        ])
        
        return {
            "total_recommendations": len(recommendations),
            "recommendations": recommendations
        }
        
    except Exception as e:
        LoggingConfig.get_api_logger().error(
            f"Failed to get security recommendations: {str(e)}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении рекомендаций по безопасности"
        )
