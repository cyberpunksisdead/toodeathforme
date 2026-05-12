# Quick Start Guide - FastAPI Blog

## 🚀 Try the Demo

The fastest way to see FastAPI Blog in action:

```bash
# Clone and install
git clone https://github.com/awestley/fastapi-blog.git
cd fastapi-blog
make install

# Run demo
./demo.sh quickstart
```

Then open:
- **Admin Panel**: http://localhost:8000/admin
- **Blog**: http://localhost:8000/blog
- **API Docs**: http://localhost:8000/docs

**Default Login**: `admin` / `Admin123!`

---

## 📚 Available Examples

Run different examples using the demo script:

### 1. Quickstart (Minimal Setup)
```bash
./demo.sh quickstart
```
Simple setup with admin panel - best for getting started.

### 2. Role-Based Access Control
```bash
./demo.sh roles
```
Demonstrates multiple users with different permissions:
- `admin` / `password` - Full access
- `editor` / `password` - Can edit, cannot delete
- `viewer` / `password` - Read-only

### 3. Internationalization (i18n)
```bash
./demo.sh i18n
```
Multi-language admin panel (English/Русский).

### 4. Full Featured
```bash
./demo.sh full
```
All features enabled: i18n, custom fields, roles, and more.

---

## 🛠️ Using Makefile

Alternatively, use make commands:

```bash
# Install dependencies
make install

# Run quickstart example
make run_quickstart

# Run roles example
make run_admin_roles

# Run i18n example
make run_admin_i18n

# Run full featured example
make run_admin_full

# Run tests
make test

# Lint and format
make lint
make format
```

---

## 📝 Basic Usage in Your Project

### Installation

```bash
pip install fastapi-blog
```

### Minimal Example

```python
from fastapi import FastAPI
import fastapi_blog

app = FastAPI()

# Add blog functionality
fastapi_blog.add_blog_to_fastapi(app, prefix="blog")

# Add admin panel
fastapi_blog.add_admin_to_app(
    app,
    admin_username="admin",
    admin_password="change-me",
    secret_key="your-secret-key",
)
```

That's it! Now you have:
- Blog at `/blog`
- Admin panel at `/admin`
- Automatic database initialization

### Create Your First Post

Create `posts/hello-world.md`:

```markdown
---
title: Hello World
date: 2024-01-15
tags: [welcome, first-post]
published: true
---

Welcome to my blog!

This is my first post using **FastAPI Blog**.

```python
print("Hello, World!")
```
```

Restart the server and visit:
- http://localhost:8000/blog - See your post
- http://localhost:8000/admin - Manage posts

---

## 🔑 Authentication

### Default Credentials

The quickstart examples use default credentials:
- **Username**: `admin`
- **Password**: `Admin123!`

⚠️ **IMPORTANT**: Change these in production!

### Custom Authentication

```python
from fastapi import FastAPI
import fastapi_blog

app = FastAPI()

fastapi_blog.add_admin_to_app(
    app,
    admin_username="your_username",
    admin_password="your_secure_password",
    secret_key="your-random-secret-key",
    database_url="sqlite:///./blog.db",  # or PostgreSQL
)
```

---

## 🌍 Internationalization

Enable multi-language support:

```python
fastapi_blog.add_admin_to_app(
    app,
    i18n_enabled=True,
    i18n_default_locale="ru",  # Default language
    i18n_locales=["en", "ru"],  # Available languages
)
```

Supported out-of-the-box:
- 🇬🇧 English (en)
- 🇷🇺 Russian (ru)

---

## 📦 Features

### Blog Features
- 📝 Markdown posts with YAML frontmatter
- 🎨 Syntax highlighting for code blocks
- 🏷️ Tags and categories
- 📅 Date-based organization
- 🔍 SEO-friendly URLs
- 📱 Responsive design

### Admin Panel Features
- ✨ Modern, beautiful UI (powered by starlette-admin)
- 👥 User management
- 📝 Post management
- 🔒 Role-based access control
- 🌍 i18n support (EN/RU)
- 📦 Custom fields (Markdown, Tags, Slugs)
- 🔍 Search and filtering
- 📄 Pagination

### Security
- 🔒 Bcrypt password hashing
- 🎪 Session-based authentication
- 🔐 CSRF protection
- 🛡️ HTML sanitization

---

## 📚 Documentation

For more detailed documentation, see:

- **Russian Guide**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **Architecture**: [ARCHITECTURE_CONSOLIDATION_PLAN.md](ARCHITECTURE_CONSOLIDATION_PLAN.md)
- **Progress**: [docs/ARCHITECTURE_CONSOLIDATION_PROGRESS.md](docs/ARCHITECTURE_CONSOLIDATION_PROGRESS.md)
- **Examples**: [tests/examples/](tests/examples/)

---

## ❓ Troubleshooting

### Port Already in Use

```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Database Errors

```bash
# Remove database and restart
rm -rf tests/examples/data/*.db
./demo.sh quickstart
```

### Import Errors

```bash
# Reinstall dependencies
make install
```

---

## 👤 Support

If you have questions or issues:

1. Check the [examples](tests/examples/)
2. Read the [documentation](docs/)
3. Open an issue on GitHub

---

## 🚀 Next Steps

After running the demo:

1. Explore the admin panel
2. Create your first blog post
3. Customize templates and styles
4. Add more features from examples
5. Deploy to production

Enjoy building with FastAPI Blog! 🎉
