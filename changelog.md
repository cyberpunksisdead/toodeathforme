# Changelog

## 0.8.1 - 2026-05-13 (Unreleased)

**Security and Stability Update**

### Security Fixes

* **Password Security Improvements**: Complete password security overhaul [#security]
  - Fixed critical `lru_cache` bug by adding `maxsize` parameter to prevent memory leaks
  - Added password hashing to admin user view using bcrypt
  - Implemented password validation (8-128 chars) with bcrypt truncation handling
  - Added clear error messages for password validation failures
  - Fixed password hashing with lazy initialization to prevent startup issues

* **Authentication Fixes**: Critical authentication improvements [#security]
  - Fixed critical bug where `auth_func` was used before definition
  - Fixed authentication type error and enforced security checks
  - Fixed `optional_authentication` to handle missing session gracefully
  - Improved admin authentication with comprehensive examples

### Bug Fixes

* **Admin Panel Fixes**: Various admin panel stability improvements [#bugfix]
  - Fixed deprecated `on_event` causing CI failure (migrated to lifespan)
  - Fixed `TemplateResponse` parameter order in `HomeView`
  - Fixed timezone comparison in `MarkdownPost.list_all`
  - Added error handling for `HomeView` post loading
  - Fixed `HomeView` to configure posts directory correctly
  - Fixed import path in `HomeView`

* **CI/CD Fixes**: Complete CI/CD pipeline fixes [#ci]
  - Fixed all ruff linting errors for CI compliance
  - Fixed mypy type errors in admin module
  - Used modern Python 3.12+ type syntax (`dict | None`)
  - Fixed code formatting for ruff compliance
  - Suppressed bandit warning for dev password

### New Features

* **RBAC (Role-Based Access Control)**: Advanced permission system [#feature]
  - Added `RoleBasedAuthProvider` for role-based permissions
  - Support for multiple roles: admin, editor, viewer
  - Fine-grained access control per view and action

* **Markdown Virtual Model**: File-based storage improvements [#feature]
  - Added `MarkdownPost` virtual model for file-based storage
  - Better integration between file-based posts and admin UI
  - Improved post listing and filtering

* **Custom Home Page**: Enhanced admin dashboard [#feature]
  - Added custom home page with blog statistics
  - Displays recent posts and key metrics
  - Configurable posts directory

### Improvements

* **Admin Panel Configuration**: Better defaults and initialization [#improvement]
  - Changed admin default URL from `/dashboard` to `/admin`
  - Fixed admin initialization and added demo tools
  - Added example blog posts for home page demo
  - Added data directory to `.gitignore`

### Documentation

* **Comprehensive Documentation**: Major documentation improvements [#docs]
  - Added comprehensive database documentation (`docs/DATABASE.md`)
  - Clarified admin panel vs REST API architecture in README
  - Added architecture consolidation plan documentation
  - Added cache bug fix documentation
  - Added password security fix documentation with UX improvements
  - Added CI lint fixes documentation
  - Added complete CI fix documentation
  - Added mission accomplished summary
  - Added CI debugging guide and next steps
  - Added CI failure analysis documentation
  - Fixed duplicate option numbering in README

## 0.8.0 - 2026-05-12

**Architecture Consolidation Update**

### New Features

* **Optional REST API**: Added `include_api` parameter to `add_blog_to_fastapi()` [#consolidation]
  - REST API is now disabled by default for better security
  - Can be enabled with `include_api=True`
  - Added `api_prefix` and `api_require_auth` parameters for configuration

* **Standalone API Router**: New `get_api_router()` function in `editor` module [#consolidation]
  - Returns configured APIRouter for flexible integration
  - Can be used independently from `add_blog_to_fastapi()`
  - Supports custom prefixes, authentication, and directory settings

### Deprecations

* **UI parameter deprecated**: The `ui` parameter in `add_editor_to_app()` is deprecated [#consolidation]
  - Will be removed in version 1.0.0
  - Users should migrate to `add_admin_to_app()` for admin interface
  - REST API remains available via `include_api` parameter or `get_api_router()`
  - DeprecationWarning emitted when `ui=True` is used

### Breaking Changes

* None (fully backwards compatible with 0.7.x)

### Migration Guide

#### Old way (deprecated):
```python
from fastapi_blog import add_editor_to_app
app = add_editor_to_app(app, ui=True)  # ⚠️ Deprecated
```

#### New way (recommended):
```python
# Option 1: Use modern admin panel
from fastapi_blog.admin import add_admin_to_app
app = add_admin_to_app(app)

# Option 2: Enable REST API via add_blog_to_fastapi
from fastapi_blog import add_blog_to_fastapi
add_blog_to_fastapi(app, include_api=True)

# Option 3: Use get_api_router directly
from fastapi_blog.editor import get_api_router
api_router = get_api_router(require_auth=True)
app.include_router(api_router, prefix="/api/posts")
```

* **Internationalization (i18n)**: Full i18n support in admin panel [#consolidation]
  - Added `i18n_enabled`, `i18n_default_locale`, and `i18n_locales` parameters
  - Support for EN/RU out of the box (uses starlette-admin translations)
  - Language switcher in admin interface when multiple locales configured
  - Added dependency: `starlette-admin[i18n]` (includes babel)

* **Custom Fields**: New field types for better admin UX [#consolidation]
  - `MarkdownField`: Enhanced textarea optimized for markdown (20+ rows, preview)
  - `TagsField`: Comma-separated tags with smart conversion and badge display
  - `SlugField`: URL-safe slug validation with automatic lowercase
  - All fields properly typed and compatible with starlette-admin

### Documentation

* Added `ARCHITECTURE_CONSOLIDATION_PROGRESS.md` with migration guide
* Updated docstrings with deprecation notices and examples
* Added examples:
  - `tests/examples/api_optional.py` - Optional REST API usage
  - `tests/examples/admin_i18n.py` - i18n configuration
  - `tests/examples/admin_full_featured.py` - All features combined

## 0.7.0 - 2025-09-18

**Major Update: Modernized Dependencies and Development Environment**

* Updated Python requirement to 3.12+ (added Python 3.13 support)
* Updated all dependencies to latest versions:
  - FastAPI: 0.109.2 → 0.115.0+
  - Uvicorn: 0.27.1 → 0.35.0+
  - Ruff: 0.2.2 → 0.8.0+
  - MyPy: 1.8.0 → 1.13.0+
  - Pytest: 8.0.1 → 8.3.0+
  - Coverage: 7.4.1 → 7.6.0+
* Modernized ruff configuration with latest linting rules
* Added comprehensive GitHub Actions CI/CD workflow
* Added security scanning with safety and bandit
* Improved development tooling and code quality checks
* Full compatibility with Python 3.13.7

## 0.6.0 - 2023-03-24

* Remove staticfiles and encourage self config. PR [#40](https://github.com/pydanny/fastapi-blog/pull/40) by [@pydanny](https://github.com/pydanny).
* Posts with zero tags no longer generate errors. PR [#39](https://github.com/pydanny/fastapi-blog/pull/39) by [@pydanny](https://github.com/pydanny).

## 0.6.0 - 2023-03-24

* Add tutorial for pages. PR [#36](https://github.com/pydanny/fastapi-blog/pull/36) by [@pydanny](https://github.com/pydanny).
* Add tutorial for blog entries. PR [#35](https://github.com/pydanny/fastapi-blog/pull/35) by [@pydanny](https://github.com/pydanny).
* Allow for control over if statics are mounted. PR [#31](https://github.com/pydanny/fastapi-blog/pull/31) by [@pydanny](https://github.com/pydanny).
* Fix markdown issue with pygments (#22). Thanks to @pydanny
* Add header permalinks to rendered markdown (#22). Thanks to @pydanny

## 0.5.0 - 2023-03-08

- Added continuous integration (#19). Thanks to @pydanny
- Remove RSS feed as it needs a complete rebuild. Thanks to @pydanny
- Use uv for local installation. Thanks to @pydanny
- Inform PyPI the changelog is at changelog.md, not CHANGELOG. Thanks to @pydanny

## 0.4.0 - 2024-03-01

- Document how to use pages (#3) and added sample `about.md` page. Thanks to @pydanny
- Standardize path arguments with `_id` suffix (#7) Thanks to @pydanny
- Initial tests for helpers.py, for #10. Thanks to @pydanny!
- Remove hardcoded favorites list, issue #13. Thanks to @pydanny!

## 0.3.0 - 2024-02-29

- Docker thanks to @audreyfeldroy!
- Installation and usage instructions for localdev and docker. Thanks to @audreyfeldroy!
- Made templates overloadable (issue #2) thanks to @pydanny!
- Added more example apps thanks to @pydanny!

## 0.2.0 - 2024-02-25

- Cleanup

## 0.1.0 - 2024-02-25

- Inception
