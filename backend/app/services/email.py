"""
Сервис для отправки email уведомлений.
"""

import smtplib
import secrets
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database.crud import user as user_crud


class EmailService:
    """Сервис для отправки email уведомлений."""
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.email_from = settings.email_from
        self.email_from_name = settings.email_from_name
    
    def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Отправка email через SMTP."""
        try:
            # Проверяем настройки
            if not self.smtp_username or not self.smtp_password or not self.email_from:
                print("Email настройки не настроены. Пропускаем отправку email.")
                return False
            
            # Создаем сообщение
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.email_from_name} <{self.email_from}>"
            msg['To'] = to_email
            
            # Добавляем текстовую версию
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Добавляем HTML версию
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Отправляем email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Ошибка отправки email: {str(e)}")
            return False
    
    def generate_reset_token(self) -> str:
        """Генерация токена для сброса пароля."""
        return secrets.token_urlsafe(32)
    
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str = None) -> bool:
        """Отправка email для сброса пароля."""
        
        # URL для сброса пароля (будет настроен в frontend)
        reset_url = f"http://localhost:5173/reset-password?token={reset_token}"
        
        # Определяем имя пользователя
        display_name = user_name if user_name else "Пользователь"
        
        # HTML версия письма
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Сброс пароля - Роль</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 500;
                    margin: 20px 0;
                }}
                .button:hover {{
                    background: #5a67d8;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e2e8f0;
                    font-size: 14px;
                    color: #64748b;
                }}
                .warning {{
                    background: #fef3cd;
                    border: 1px solid #fde68a;
                    color: #92400e;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎭 Роль</h1>
                <p>Сброс пароля</p>
            </div>
            
            <div class="content">
                <h2>Здравствуйте, {display_name}!</h2>
                
                <p>Вы запросили сброс пароля для вашего аккаунта в системе "Роль".</p>
                
                <p>Для создания нового пароля нажмите на кнопку ниже:</p>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Сбросить пароль</a>
                </div>
                
                <p>Или скопируйте и вставьте эту ссылку в ваш браузер:</p>
                <p style="word-break: break-all; background: #e2e8f0; padding: 10px; border-radius: 4px; font-family: monospace;">
                    {reset_url}
                </p>
                
                <div class="warning">
                    <strong>⚠️ Важно:</strong>
                    <ul>
                        <li>Ссылка действительна в течение 1 часа</li>
                        <li>Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо</li>
                        <li>Никому не передавайте эту ссылку</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>С уважением,<br>Команда "Роль"</p>
                    <p><small>Это автоматическое письмо, не отвечайте на него.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Текстовая версия письма
        text_content = f"""
        Сброс пароля - Роль
        
        Здравствуйте, {display_name}!
        
        Вы запросили сброс пароля для вашего аккаунта в системе "Роль".
        
        Для создания нового пароля перейдите по ссылке:
        {reset_url}
        
        ВАЖНО:
        - Ссылка действительна в течение 1 часа
        - Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо
        - Никому не передавайте эту ссылку
        
        С уважением,
        Команда "Роль"
        
        Это автоматическое письмо, не отвечайте на него.
        """
        
        subject = "Сброс пароля - Роль"
        
        return self._send_email(to_email, subject, html_content, text_content)
    
    def send_password_changed_notification(self, to_email: str, user_name: str = None) -> bool:
        """Отправка уведомления об успешной смене пароля."""
        
        display_name = user_name if user_name else "Пользователь"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Пароль изменен - Роль</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e2e8f0;
                    font-size: 14px;
                    color: #64748b;
                }}
                .success {{
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    color: #155724;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎭 Роль</h1>
                <p>Пароль успешно изменен</p>
            </div>
            
            <div class="content">
                <h2>Здравствуйте, {display_name}!</h2>
                
                <div class="success">
                    <strong>✅ Пароль успешно изменен</strong>
                    <p>Ваш пароль был успешно изменен {datetime.now().strftime('%d.%m.%Y в %H:%M')}.</p>
                </div>
                
                <p>Если вы не изменяли пароль, немедленно свяжитесь с нами.</p>
                
                <div class="footer">
                    <p>С уважением,<br>Команда "Роль"</p>
                    <p><small>Это автоматическое письмо, не отвечайте на него.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Пароль изменен - Роль
        
        Здравствуйте, {display_name}!
        
        Ваш пароль был успешно изменен {datetime.now().strftime('%d.%m.%Y в %H:%M')}.
        
        Если вы не изменяли пароль, немедленно свяжитесь с нами.
        
        С уважением,
        Команда "Роль"
        """
        
        subject = "Пароль изменен - Роль"
        
        return self._send_email(to_email, subject, html_content, text_content)


# Глобальный экземпляр сервиса
email_service = EmailService()
