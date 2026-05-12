"""Admin panel integration for FastAPI Blog.

Provides starlette-admin based administration interface with:
- User management
- Post management with WYSIWYG editor
- Simple authentication provider
"""

import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin

from .auth_provider import SimpleAuthProvider
from .database import create_engine_and_session, init_db
from .models import Post, User
from .views import PostModelView, UserModelView


# File-based views removed - using CustomView instead

__all__ = [
    "add_admin_to_app",
    "User",
    "Post",
    "SimpleAuthProvider",
    "UserModelView",
    "PostModelView",
]


def add_admin_to_app(
    app: FastAPI,
    *,
    base_url: str = "/dashboard",
    title: str = "Admin Panel",
    database_url: str | None = None,
    admin_username: str = "admin",
    admin_password: str = "Admin123!",
    secret_key: str | None = None,
    add_session_middleware: bool = True,
    init_database: bool = True,
) -> Admin:
    """Add starlette-admin panel to FastAPI application.

    Args:
      app: FastAPI application instance
      base_url: Base URL for admin panel (default: '/dashboard')
      title: Admin panel title
      database_url: Database URL (default: from DATABASE_URL env or SQLite)
      admin_username: Admin username for login (default: 'admin')
      admin_password: Admin password for login (default: 'Admin123!')
      secret_key: Secret key for sessions (default: from SECRET_KEY env)
      add_session_middleware: Whether to add SessionMiddleware (default: True)
      init_database: Whether to initialize database on startup (default: True)

    Returns:
      Admin instance

    Example:
      ```python
      from fastapi import (
          FastAPI,
      )
      from fastapi_blog.admin import (
          add_admin_to_app,
      )

      app = FastAPI()
      admin = add_admin_to_app(
          app,
          title="My Blog Admin",
          admin_password="SuperSecret123!",
      )
      ```

    """
    # Get secret key
    if secret_key is None:
        secret_key = os.getenv(
            "SECRET_KEY", "change-me-in-production-please-use-strong-secret"
        )

    # Add session middleware if needed (must be added AFTER CORS)
    if add_session_middleware:
        app.add_middleware(SessionMiddleware, secret_key=secret_key)

    # Create engine and session
    engine, session_factory = create_engine_and_session(database_url)

    # Note: Database initialization should be done in app lifespan or startup event
    # If init_database=True, caller should handle init_db(engine) in their startup
    if init_database:
        # Store engine for later initialization
        app.state.admin_engine = engine

    # Create auth provider
    auth_provider = SimpleAuthProvider(
        username=admin_username,
        password=admin_password,
        redirect_after_login=f"{base_url}/user/list",
    )

    # Get templates directory for custom templates
    from pathlib import Path

    import fastapi_blog

    pkg_path = Path(fastapi_blog.__file__).parent
    templates_dir = str(pkg_path / "admin" / "templates")

    # Create admin instance
    admin = Admin(
        engine,
        title=title,
        base_url=base_url,
        auth_provider=auth_provider,
        templates_dir=templates_dir,
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )

    # Add model views
    admin.add_view(UserModelView(User, icon="fa fa-users"))

    # Add markdown CRUD views
    from .markdown_crud import (
        MarkdownCreateView,
        MarkdownEditView,
        MarkdownListView,
        get_posts_directory,
    )

    posts_dir = get_posts_directory()

    # Add list view (shows in menu)
    admin.add_view(MarkdownListView(posts_dir=posts_dir))

    # Add edit and create views (don't show in menu)
    admin.add_view(MarkdownEditView(posts_dir=posts_dir))
    admin.add_view(MarkdownCreateView(posts_dir=posts_dir))

    # Mount admin to app
    admin.mount_to(app)
    print(f"✓ Admin panel mounted at {base_url}")
    print("✓ Markdown CRUD API available at /api/posts (authenticated)")

    return admin
