"""Admin panel integration for FastAPI Blog.

Provides starlette-admin based administration interface with:
- User management
- Post management with WYSIWYG editor
- Simple authentication provider
"""

import os
import pathlib
import warnings

from babel.support import Translations
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin
from starlette_admin.i18n import I18nConfig

from .auth_provider import SimpleAuthProvider
from .database import create_engine_and_session, init_db
from .fields import MarkdownField, SlugField, TagsField
from .models import Post, User


try:
    from starlette_admin.i18n import lazy_gettext as _
except ImportError:
    # Fallback if i18n is not available
    def _(message: str) -> str:
        return message


def _load_custom_translations():
    """Load and merge custom translations with starlette-admin's built-in translations."""
    import starlette_admin.i18n

    # Get path to our translations directory
    package_dir = pathlib.Path(__file__).parent.parent
    translations_dir = package_dir / "translations"

    if not translations_dir.exists():
        return

    # Load translations for each locale
    for locale in ["en", "ru"]:
        locale_dir = translations_dir / locale / "LC_MESSAGES"
        mo_file = locale_dir / "admin.mo"

        if mo_file.exists():
            try:
                # Load our custom translations
                with open(mo_file, "rb") as f:
                    custom_trans = Translations(f, domain="admin")

                # Merge with starlette-admin's built-in translations if they exist
                if locale in starlette_admin.i18n.translations:
                    # Add starlette-admin's translations as fallback
                    custom_trans.add_fallback(starlette_admin.i18n.translations[locale])

                # Replace the translations in starlette-admin's dict
                starlette_admin.i18n.translations[locale] = custom_trans
            except Exception as e:
                warnings.warn(f"Failed to load {locale} translations: {e}")


# Load custom translations at module import time, before views are imported
_load_custom_translations()

# Set a default locale context for lazy_gettext evaluation during import
# This will be used when view class attributes are defined
import starlette_admin.i18n  # noqa: E402


starlette_admin.i18n.set_locale(
    "en"
)  # Default to English, will be overridden per request

# Import views after translations are loaded and locale is set
from .views import HomeView, PostModelView, UserModelView  # noqa: E402


# File-based views removed - using CustomView instead

__all__ = [
    "add_admin_to_app",
    "User",
    "Post",
    "SimpleAuthProvider",
    "UserModelView",
    "PostModelView",
    "HomeView",
    "MarkdownField",
    "TagsField",
    "SlugField",
]


def _has_session_middleware(app: FastAPI) -> bool:
    """Check if SessionMiddleware is already added to the app.

    Args:
      app: FastAPI application instance

    Returns:
      True if SessionMiddleware is already added, False otherwise

    """
    for middleware in app.user_middleware:
        if middleware.cls == SessionMiddleware:
            return True
    return False


def add_admin_to_app(
    app: FastAPI,
    *,
    base_url: str = "/admin",
    title: str = "Admin Panel",
    database_url: str | None = None,
    admin_username: str = "admin",
    admin_password: str = "Admin123!",
    secret_key: str | None = None,
    add_session_middleware: bool = True,
    init_database: bool = True,
    i18n_enabled: bool = True,
    i18n_default_locale: str = "en",
    i18n_locales: list[str] | None = None,
) -> Admin:
    """Add starlette-admin panel to FastAPI application.

    Args:
      app: FastAPI application instance
      base_url: Base URL for admin panel (default: '/admin')
      title: Admin panel title
      database_url: Database URL (default: from DATABASE_URL env or SQLite)
      admin_username: Admin username for login (default: 'admin')
      admin_password: Admin password for login (default: 'Admin123!')
      secret_key: Secret key for sessions (default: from SECRET_KEY env)
      add_session_middleware: Whether to add SessionMiddleware (default: True)
      init_database: Whether to initialize database on startup (default: True)
      i18n_enabled: Enable internationalization (default: True)
      i18n_default_locale: Default locale (default: 'en')
      i18n_locales: List of available locales (default: ['en', 'ru'])

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

      # English only
      admin = add_admin_to_app(
          app,
          title="My Blog Admin",
          admin_password="SuperSecret123!",
          i18n_locales=[
              "en"
          ],
      )

      # Russian by default with EN/RU switcher
      admin = add_admin_to_app(
          app,
          title="Админ-панель блога",
          i18n_default_locale="ru",
          i18n_locales=[
              "en",
              "ru",
          ],
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
        if _has_session_middleware(app):
            warnings.warn(
                "SessionMiddleware is already added to the application. "
                "Set add_session_middleware=False to avoid duplication. "
                "Skipping duplicate middleware addition.",
                UserWarning,
                stacklevel=2,
            )
        else:
            app.add_middleware(SessionMiddleware, secret_key=secret_key)

    # Create engine and session
    engine, session_factory = create_engine_and_session(database_url)

    # Initialize database if requested
    if init_database:
        # Store engine for later access
        app.state.admin_engine = engine

        # Use lifespan event for async initialization (modern approach)
        from contextlib import asynccontextmanager

        # Check if app already has a lifespan
        original_lifespan = getattr(app.router, "lifespan_context", None)

        @asynccontextmanager
        async def admin_lifespan(app):
            # Startup: initialize database
            await init_db(engine)
            print("✓ Admin database initialized")
            print(f"✓ Admin panel: http://localhost:8000{base_url}")
            print(f"✓ Login: username='{admin_username}' password='{admin_password}'")

            # Call original lifespan if exists
            if original_lifespan:
                async with original_lifespan(app):
                    yield
            else:
                yield

            # Shutdown: cleanup if needed

        # Replace app's lifespan
        app.router.lifespan_context = admin_lifespan

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

    # Configure i18n if enabled
    i18n_config = None
    if i18n_enabled:
        # Custom translations are already loaded at module import time
        if i18n_locales is None:
            i18n_locales = ["en", "ru"]
        i18n_config = I18nConfig(
            default_locale=i18n_default_locale,
            language_switcher=i18n_locales if len(i18n_locales) > 1 else None,
        )

    # Create admin instance
    # Set locale context to default locale for translation
    from starlette_admin.i18n import gettext, set_locale

    set_locale(i18n_default_locale)

    # Get translated labels for the default locale
    home_label = gettext("Home")
    user_label_singular = gettext("User")
    user_label_plural = gettext("Users")
    posts_label = gettext("Posts")

    admin = Admin(
        engine,
        title=title,
        base_url=base_url,
        auth_provider=auth_provider,
        templates_dir=templates_dir,
        i18n_config=i18n_config,
        debug=os.getenv("DEBUG", "false").lower() == "true",
        index_view=HomeView(label=home_label, icon="fa fa-home"),
    )

    # Add model views with translated labels
    # Override label and name to use translated values from default locale
    user_view = UserModelView(User, icon="fa fa-users")
    user_view.label = user_label_singular
    user_view.name = user_label_singular  # Used in "New %(name)s" button template
    user_view.label_plural = user_label_plural
    admin.add_view(user_view)

    # Add markdown CRUD views
    from .markdown_crud import (
        MarkdownCreateView,
        MarkdownEditView,
        MarkdownListView,
        get_posts_directory,
    )

    posts_dir = get_posts_directory()

    # Add list view (shows in menu) with translated label
    posts_list_view = MarkdownListView(posts_dir=posts_dir)
    posts_list_view.label = posts_label
    admin.add_view(posts_list_view)

    # Add edit and create views (don't show in menu)
    admin.add_view(MarkdownEditView(posts_dir=posts_dir))
    admin.add_view(MarkdownCreateView(posts_dir=posts_dir))

    # Mount admin to app
    admin.mount_to(app)
    print(f"✓ Admin panel mounted at {base_url}")
    print("✓ Markdown CRUD API available at /api/posts (authenticated)")

    if init_database:
        print("✓ Database initialized")
    else:
        print("⚠ Database initialization disabled. Call init_db(engine) manually.")

    print(f"✓ Login: username='{admin_username}' password='{admin_password}'")
    print(f"✓ Access at: http://localhost:8000{base_url}")

    return admin
