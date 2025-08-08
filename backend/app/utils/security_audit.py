"""
Утилиты для проведения security audit.
"""

import re
import hashlib
import secrets
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from app.config.settings import settings
from app.utils.logging_config import LoggingConfig


class SecurityAuditor:
    """Класс для проведения аудита безопасности."""
    
    def __init__(self):
        """Инициализация аудитора безопасности."""
        self.audit_results: List[Dict[str, Any]] = []
        self.security_logger = LoggingConfig.get_api_logger()
    
    def audit_all(self) -> Dict[str, Any]:
        """
        Проводит полный аудит безопасности.
        
        Returns:
            Результаты аудита безопасности
        """
        self.audit_results.clear()
        
        # Проверка конфигурации
        self._audit_configuration()
        
        # Проверка паролей и секретов
        self._audit_secrets()
        
        # Проверка файловой безопасности
        self._audit_file_security()
        
        # Проверка зависимостей
        self._audit_dependencies()
        
        # Проверка CORS настроек
        self._audit_cors_settings()
        
        # Проверка rate limiting
        self._audit_rate_limiting()
        
        # Генерация отчета
        return self._generate_security_report()
    
    def _audit_configuration(self):
        """Проверка конфигурации безопасности."""
        issues = []
        
        # Проверка DEBUG режима
        if settings.debug:
            issues.append({
                "severity": "HIGH",
                "category": "Configuration",
                "issue": "DEBUG режим включен в production",
                "description": "DEBUG режим может раскрыть чувствительную информацию",
                "recommendation": "Отключить DEBUG в production"
            })
        
        # Проверка секретного ключа
        if not settings.secret_key or len(settings.secret_key) < 32:
            issues.append({
                "severity": "CRITICAL",
                "category": "Configuration", 
                "issue": "Слабый секретный ключ",
                "description": "Секретный ключ слишком короткий или отсутствует",
                "recommendation": "Использовать криптографически стойкий ключ длиной не менее 32 символов"
            })
        
        # Проверка срока действия токенов
        if settings.access_token_expire_minutes > 60:
            issues.append({
                "severity": "MEDIUM",
                "category": "Configuration",
                "issue": "Долгий срок действия токенов",
                "description": f"Токены действуют {settings.access_token_expire_minutes} минут",
                "recommendation": "Рассмотреть сокращение времени жизни токенов"
            })
        
        self.audit_results.extend(issues)
    
    def _audit_secrets(self):
        """Проверка секретов и паролей."""
        issues = []
        
        # Проверка на использование слабых секретов
        weak_patterns = [
            r'password.*=.*["\'].*123.*["\']',
            r'secret.*=.*["\'].*secret.*["\']',
            r'key.*=.*["\'].*key.*["\']',
            r'token.*=.*["\'].*token.*["\']'
        ]
        
        # Проверяем файлы конфигурации
        config_files = [
            Path("backend/.env"),
            Path("backend/env.example"),
            Path("backend/app/config/settings.py")
        ]
        
        for file_path in config_files:
            if file_path.exists():
                content = file_path.read_text()
                
                for pattern in weak_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append({
                            "severity": "HIGH",
                            "category": "Secrets",
                            "issue": f"Потенциально слабый секрет в {file_path}",
                            "description": "Обнаружен потенциально слабый секрет или пароль",
                            "recommendation": "Использовать криптографически стойкие секреты"
                        })
        
        # Проверка на наличие секретов в git
        gitignore_path = Path("backend/.gitignore")
        if gitignore_path.exists():
            gitignore_content = gitignore_path.read_text()
            if ".env" not in gitignore_content:
                issues.append({
                    "severity": "HIGH",
                    "category": "Secrets",
                    "issue": ".env файл может попасть в git",
                    "description": ".env файл не добавлен в .gitignore",
                    "recommendation": "Добавить .env в .gitignore"
                })
        
        self.audit_results.extend(issues)
    
    def _audit_file_security(self):
        """Проверка файловой безопасности."""
        issues = []
        
        # Проверка прав доступа к критичным файлам
        critical_files = [
            Path("backend/.env"),
            Path("backend/app/config/settings.py"),
            Path("backend/logs/")
        ]
        
        for file_path in critical_files:
            if file_path.exists():
                # В production нужно проверять реальные права доступа
                # Здесь упрощенная проверка
                if file_path.suffix == ".env":
                    issues.append({
                        "severity": "MEDIUM",
                        "category": "File Security",
                        "issue": f"Проверить права доступа к {file_path}",
                        "description": "Файл содержит чувствительные данные",
                        "recommendation": "Установить права доступа 600 (только владелец)"
                    })
        
        # Проверка на наличие временных файлов
        temp_patterns = ["*.tmp", "*.temp", "*~", "*.bak"]
        backend_path = Path("backend/")
        
        for pattern in temp_patterns:
            temp_files = list(backend_path.rglob(pattern))
            if temp_files:
                issues.append({
                    "severity": "LOW",
                    "category": "File Security",
                    "issue": f"Найдены временные файлы: {pattern}",
                    "description": f"Обнаружено {len(temp_files)} временных файлов",
                    "recommendation": "Удалить временные файлы из production"
                })
        
        self.audit_results.extend(issues)
    
    def _audit_dependencies(self):
        """Проверка зависимостей на уязвимости."""
        issues = []
        
        # Проверка устаревших зависимостей
        requirements_file = Path("backend/requirements.txt")
        if requirements_file.exists():
            content = requirements_file.read_text()
            
            # Список потенциально проблемных пакетов
            risky_patterns = [
                r'fastapi==0\.[0-9]+\.[0-9]+',  # Очень старые версии FastAPI
                r'sqlalchemy==1\.[0-9]+\.[0-9]+',  # SQLAlchemy 1.x
            ]
            
            for pattern in risky_patterns:
                if re.search(pattern, content):
                    issues.append({
                        "severity": "MEDIUM",
                        "category": "Dependencies",
                        "issue": "Устаревшие зависимости",
                        "description": f"Найдены потенциально устаревшие зависимости",
                        "recommendation": "Обновить зависимости до последних стабильных версий"
                    })
        
        # Проверка на избыточные зависимости
        if requirements_file.exists():
            lines = requirements_file.read_text().split('\n')
            package_count = len([line for line in lines if line.strip() and not line.startswith('#')])
            
            if package_count > 50:
                issues.append({
                    "severity": "LOW",
                    "category": "Dependencies",
                    "issue": f"Много зависимостей ({package_count})",
                    "description": "Большое количество зависимостей увеличивает поверхность атаки",
                    "recommendation": "Регулярно проверять необходимость всех зависимостей"
                })
        
        self.audit_results.extend(issues)
    
    def _audit_cors_settings(self):
        """Проверка настроек CORS."""
        issues = []
        
        # В реальном приложении нужно проверить actual CORS конфигурацию
        # Здесь упрощенная проверка на основе кода
        main_file = Path("backend/app/main.py")
        if main_file.exists():
            content = main_file.read_text()
            
            if 'allow_origins=["*"]' in content:
                issues.append({
                    "severity": "HIGH",
                    "category": "CORS",
                    "issue": "CORS настроен на разрешение всех доменов",
                    "description": "allow_origins=['*'] разрешает запросы с любых доменов",
                    "recommendation": "Указать конкретные разрешенные домены"
                })
            
            if 'allow_methods=["*"]' in content:
                issues.append({
                    "severity": "MEDIUM",
                    "category": "CORS",
                    "issue": "CORS разрешает все HTTP методы",
                    "description": "allow_methods=['*'] может быть избыточным",
                    "recommendation": "Разрешить только необходимые HTTP методы"
                })
        
        self.audit_results.extend(issues)
    
    def _audit_rate_limiting(self):
        """Проверка настроек rate limiting."""
        issues = []
        
        # Проверка настроек rate limiting в middleware
        middleware_file = Path("backend/app/middleware/auth_middleware.py")
        if middleware_file.exists():
            content = middleware_file.read_text()
            
            # Ищем настройки rate limiting
            rate_limit_match = re.search(r'rate_limit_requests=(\d+)', content)
            if rate_limit_match:
                rate_limit = int(rate_limit_match.group(1))
                if rate_limit > 1000:
                    issues.append({
                        "severity": "MEDIUM",
                        "category": "Rate Limiting",
                        "issue": f"Высокий лимит запросов ({rate_limit})",
                        "description": "Лимит запросов может быть слишком высоким для защиты от DoS",
                        "recommendation": "Рассмотреть снижение лимита запросов"
                    })
            else:
                issues.append({
                    "severity": "MEDIUM",
                    "category": "Rate Limiting",
                    "issue": "Rate limiting не настроен",
                    "description": "Отсутствует защита от избыточных запросов",
                    "recommendation": "Настроить rate limiting для защиты от DoS атак"
                })
        
        self.audit_results.extend(issues)
    
    def _generate_security_report(self) -> Dict[str, Any]:
        """Генерирует итоговый отчет по безопасности."""
        
        # Подсчитываем статистику
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        category_counts = {}
        
        for issue in self.audit_results:
            severity = issue["severity"]
            category = issue["category"]
            
            severity_counts[severity] += 1
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Вычисляем общий уровень безопасности
        total_issues = len(self.audit_results)
        critical_issues = severity_counts["CRITICAL"]
        high_issues = severity_counts["HIGH"]
        
        if critical_issues > 0:
            security_level = "CRITICAL"
        elif high_issues > 3:
            security_level = "HIGH"
        elif high_issues > 0 or severity_counts["MEDIUM"] > 5:
            security_level = "MEDIUM"
        elif total_issues > 0:
            security_level = "LOW"
        else:
            security_level = "GOOD"
        
        report = {
            "audit_date": datetime.now().isoformat(),
            "security_level": security_level,
            "total_issues": total_issues,
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "issues": self.audit_results,
            "recommendations": self._get_priority_recommendations()
        }
        
        # Логируем результаты аудита
        self.security_logger.info(
            f"Security audit completed",
            security_level=security_level,
            total_issues=total_issues,
            critical_issues=critical_issues,
            high_issues=high_issues
        )
        
        return report
    
    def _get_priority_recommendations(self) -> List[str]:
        """Получает приоритетные рекомендации."""
        recommendations = []
        
        # Критичные рекомендации
        critical_issues = [issue for issue in self.audit_results if issue["severity"] == "CRITICAL"]
        for issue in critical_issues:
            recommendations.append(f"🔴 КРИТИЧНО: {issue['recommendation']}")
        
        # Высокоприоритетные рекомендации
        high_issues = [issue for issue in self.audit_results if issue["severity"] == "HIGH"]
        for issue in high_issues[:3]:  # Показываем только первые 3
            recommendations.append(f"🟠 ВЫСОКИЙ: {issue['recommendation']}")
        
        if not recommendations:
            recommendations.append("✅ Критичных проблем безопасности не обнаружено")
        
        return recommendations


class SecurityUtils:
    """Утилиты для обеспечения безопасности."""
    
    @staticmethod
    def generate_secure_secret(length: int = 32) -> str:
        """
        Генерирует криптографически стойкий секрет.
        
        Args:
            length: Длина секрета в байтах
            
        Returns:
            Hex-представление секрета
        """
        return secrets.token_hex(length)
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Хеширует пароль с солью.
        
        Args:
            password: Пароль для хеширования
            salt: Соль (генерируется автоматически если не указана)
            
        Returns:
            Кортеж (hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        
        return password_hash.hex(), salt
    
    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """
        Проверяет пароль по хешу.
        
        Args:
            password: Проверяемый пароль
            password_hash: Хеш пароля
            salt: Соль
            
        Returns:
            True если пароль верный
        """
        computed_hash, _ = SecurityUtils.hash_password(password, salt)
        return secrets.compare_digest(computed_hash, password_hash)
    
    @staticmethod
    def validate_input(input_value: str, max_length: int = 1000) -> bool:
        """
        Базовая валидация пользовательского ввода.
        
        Args:
            input_value: Значение для проверки
            max_length: Максимальная длина
            
        Returns:
            True если ввод валиден
        """
        if not input_value or len(input_value) > max_length:
            return False
        
        # Проверка на потенциально опасные паттерны
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'<iframe',
            r'eval\(',
            r'document\.cookie'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, input_value, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Санитизирует имя файла.
        
        Args:
            filename: Исходное имя файла
            
        Returns:
            Безопасное имя файла
        """
        # Удаляем опасные символы
        safe_chars = re.sub(r'[^\w\s.-]', '', filename)
        
        # Удаляем множественные пробелы и точки
        safe_chars = re.sub(r'\.{2,}', '.', safe_chars)
        safe_chars = re.sub(r'\s+', '_', safe_chars)
        
        # Ограничиваем длину
        if len(safe_chars) > 255:
            name, ext = safe_chars.rsplit('.', 1) if '.' in safe_chars else (safe_chars, '')
            safe_chars = name[:250] + ('.' + ext if ext else '')
        
        return safe_chars.strip('._')


# Глобальный экземпляр аудитора
security_auditor = SecurityAuditor()
security_utils = SecurityUtils()
