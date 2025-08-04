#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_auth_and_projects():
    """Тестирует авторизацию и получение проектов."""
    
    # Регистрируем пользователя
    print("🔧 Регистрируем тестового пользователя...")
    register_data = {
        "username": "testfrontend",
        "email": "testfrontend@example.com", 
        "password": "password123",
        "full_name": "Test Frontend User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("✅ Пользователь зарегистрирован")
        else:
            print(f"⚠️  Пользователь уже существует (код: {response.status_code})")
    except Exception as e:
        print(f"❌ Ошибка регистрации: {e}")
    
    # Логинимся
    print("\n🔑 Авторизуемся...")
    login_data = {
        "email": "testfrontend@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens["access_token"]
            print("✅ Авторизация успешна")
            print(f"🔑 Токен: {access_token[:50]}...")
        else:
            print(f"❌ Ошибка авторизации: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Ошибка логина: {e}")
        return
    
    # Проверяем профиль
    print("\n👤 Проверяем профиль...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Профиль получен: {user['username']} ({user['email']})")
        else:
            print(f"❌ Ошибка получения профиля: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка профиля: {e}")
        return
    
    # Получаем проекты
    print("\n📁 Получаем проекты...")
    try:
        response = requests.get(f"{BASE_URL}/projects/", headers=headers)
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Проекты получены: {len(projects)} шт.")
            for project in projects:
                print(f"   📄 {project['title']} (ID: {project['id']})")
        else:
            print(f"❌ Ошибка получения проектов: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Ошибка проектов: {e}")
        return
    
    # Создаем проект
    print("\n📝 Создаем тестовый проект...")
    project_data = {
        "title": "Frontend Test Project",
        "description": "Проект для тестирования фронтенда"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/projects/", json=project_data, headers=headers)
        if response.status_code == 201:
            project = response.json()
            print(f"✅ Проект создан: {project['title']} (ID: {project['id']})")
        else:
            print(f"❌ Ошибка создания проекта: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Ошибка создания: {e}")
        return
    
    # Получаем проекты снова
    print("\n📁 Получаем проекты еще раз...")
    try:
        response = requests.get(f"{BASE_URL}/projects/", headers=headers)
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Проекты получены: {len(projects)} шт.")
            for project in projects:
                print(f"   📄 {project['title']} (ID: {project['id']})")
        else:
            print(f"❌ Ошибка получения проектов: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка проектов: {e}")
    
    print(f"\n🎯 Для тестирования фронтенда используйте:")
    print(f"   Email: testfrontend@example.com")
    print(f"   Password: password123")

if __name__ == "__main__":
    test_auth_and_projects()
