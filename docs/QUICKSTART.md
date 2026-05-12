# Quick Start Guide

## Минимальный пример для быстрого старта

### 1. Установка

```bash
pip install fastapi-blog
```

### 2. Создайте `app.py`

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import fastapi_blog

# Create necessary directories
Path("posts").mkdir(exist_ok=True)
Path("pages").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)

app = FastAPI()

# Add blog
fastapi_blog.add_blog_to_fastapi(app, prefix="blog")

# Add admin panel (auto-initializes database)
admin = fastapi_blog.add_admin_to_app(
    app,
    admin_username="admin",
    admin_password="Admin123!",  # Change this!
    secret_key="your-secret-key-here",  # Change this!
)

app.mount("/static", StaticFiles(directory="static"), name="static")
```

### 3. Запустите приложение

```bash
uvicorn app:app --reload
```

### 4. Откройте в браузере

- **Блог**: http://localhost:8000/blog
- **Админ-панель**: http://localhost:8000/dashboard
- **API документация**: http://localhost:8000/docs

### 5. Войдите в админ-панель

**Credentials по умолчанию**:
- Username: `admin`
- Password: `Admin123!`

⚠️ **Важно**: Смените пароль и secret_key в продакшене!

## Что происходит при запуске?

1. **Создаются директории** для постов, страниц и статики
2. **Инициализируется база данных** SQLite (`blog.db`)
3. **Монтируются роуты**:
   - `/blog` - публичный блог
   - `/dashboard` - админ-панель
   - `/api/posts` - REST API (требует аутентификации)
4. **Выводятся сообщения**:
   ```
   ✓ Admin panel mounted at /dashboard
   ✓ Markdown CRUD API available at /api/posts (authenticated)
   ✓ Admin database initialized
   ✓ Admin panel: http://localhost:8000/dashboard
   ✓ Login: username='admin' password='Admin123!'
   ```

## Создание первого поста

### Через админ-панель

1. Откройте http://localhost:8000/dashboard
2. Войдите (admin / Admin123!)
3. Перейдите в "Markdown Posts"
4. Нажмите "Create"
5. Заполните форму и сохраните

### Через файл

Создайте `posts/my-first-post.md`:

```markdown
---
title: "My First Post"
date: "2024-05-12"
published: true
tags:
  - hello
  - fastapi
description: "My first blog post"
---

# Hello World!

This is my first blog post using **fastapi-blog**.

## Features

- Easy setup
- Markdown support
- Admin interface
- REST API
```

Пост сразу появится на http://localhost:8000/blog

## Настройка (опционально)

### Изменить язык админки

```python
admin = fastapi_blog.add_admin_to_app(
    app,
    i18n_default_locale="ru",  # Русский по умолчанию
    i18n_locales=["en", "ru"],  # Переключатель языков
)
```

### Включить REST API для блога

```python
fastapi_blog.add_blog_to_fastapi(
    app,
    prefix="blog",
    include_api=True,  # Включить REST API
    api_require_auth=True,  # Требовать аутентификацию
)
```

### Использовать PostgreSQL вместо SQLite

```python
admin = fastapi_blog.add_admin_to_app(
    app,
    database_url="postgresql://user:pass@localhost/blogdb",
)
```

## Следующие шаги

1. Создайте несколько постов через админ-панель
2. Настройте внешний вид через custom templates
3. Добавьте страницы (About, Contact) в директорию `pages/`
4. Деплой на сервер (Heroku, Railway, VPS)

## Примеры

Больше примеров в `tests/examples/`:
- `quickstart.py` - минимальный setup
- `admin_i18n.py` - с интернационализацией
- `admin_full_featured.py` - все возможности
- `api_optional.py` - с REST API

## Troubleshooting

### Не могу войти в админку

**Проблема**: После ввода логина/пароля ничего не происходит

**Решение**: Проверьте что:
1. База данных инициализирована (смотрите логи при старте)
2. SessionMiddleware добавлен (происходит автоматически)
3. secret_key установлен

### База данных не создаётся

**Проблема**: Ошибка "Table not found"

**Решение**: Убедитесь что `init_database=True` (по умолчанию) или вручную вызовите:

```python
from fastapi_blog.admin.database import init_db

@app.on_event("startup")
async def startup():
    init_db(app.state.admin_engine)
```

### Посты не отображаются

**Проблема**: Пустая страница /blog

**Решение**: 
1. Проверьте что директория `posts/` существует
2. Создайте markdown файлы с правильным frontmatter
3. Установите `published: true` в frontmatter

## Поддержка

- GitHub Issues: https://github.com/pydanny/fastapi-blog/issues
- Документация: https://github.com/pydanny/fastapi-blog
