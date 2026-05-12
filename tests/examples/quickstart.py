"""Quick start example - minimal setup to get started.

Run this example:
    cd tests/examples
    uvicorn quickstart:app --reload

Then open:
    Blog:  http://localhost:8000/blog
    Admin: http://localhost:8000/dashboard

Login credentials:
    Username: admin
    Password: Admin123!
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import fastapi_blog


# Create necessary directories
Path("posts").mkdir(exist_ok=True)
Path("pages").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)

# Create FastAPI app
app = FastAPI(title="My Blog")

# Add blog functionality
fastapi_blog.add_blog_to_fastapi(
    app,
    prefix="blog",
    strict_frontmatter=False,
    sanitize_html=False,
)

# Add admin panel (database auto-initialized on startup)
admin = fastapi_blog.add_admin_to_app(
    app,
    title="Blog Admin",
    base_url="/dashboard",
    admin_username="admin",
    admin_password="Admin123!",
    secret_key="change-me-in-production",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Homepage with links and instructions."""
    return {
        "message": "Welcome to FastAPI Blog!",
        "links": {
            "blog": "http://localhost:8000/blog",
            "admin": "http://localhost:8000/dashboard",
            "api_docs": "http://localhost:8000/docs",
        },
        "admin_login": {
            "username": "admin",
            "password": "Admin123!",
            "note": "⚠️ Change these credentials in production!",
        },
        "first_steps": [
            "1. Go to /dashboard and login",
            "2. Create your first blog post",
            "3. View it at /blog",
        ],
    }
