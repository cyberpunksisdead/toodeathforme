# Session Middleware Duplication Fix

## Problem

When using `add_admin_to_app()`, the `SessionMiddleware` could be added twice if:

1. User manually adds `SessionMiddleware` to the app
2. Then calls `add_admin_to_app()` without setting `add_session_middleware=False`

```python
app = FastAPI()

# User adds middleware manually
app.add_middleware(SessionMiddleware, secret_key="my-key")

# Then adds admin (middleware added AGAIN by default!)
add_admin_to_app(app)  # ❌ Duplicate SessionMiddleware!
```

## Solution

Added automatic detection of duplicate `SessionMiddleware`:

### Implementation

```python
def _has_session_middleware(app: FastAPI) -> bool:
    """Check if SessionMiddleware is already added to the app."""
    for middleware in app.user_middleware:
        if middleware.cls == SessionMiddleware:
            return True
    return False

def add_admin_to_app(...):
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
```

### Behavior

1. **Automatic Detection**: Checks if `SessionMiddleware` is already present
2. **Warning Issued**: Issues `UserWarning` if duplicate detected
3. **Skips Addition**: Does NOT add duplicate middleware
4. **Guidance Provided**: Warns user to set `add_session_middleware=False`

## Usage Examples

### ✅ Correct: No manual middleware
```python
from fastapi import FastAPI
from fastapi_blog.admin import add_admin_to_app

app = FastAPI()

# Let add_admin_to_app handle middleware
add_admin_to_app(app)  # ✅ Adds SessionMiddleware automatically
```

### ✅ Correct: Manual middleware with explicit False
```python
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi_blog.admin import add_admin_to_app

app = FastAPI()

# Add middleware manually
app.add_middleware(SessionMiddleware, secret_key="my-key")

# Tell add_admin_to_app not to add it again
add_admin_to_app(
    app,
    add_session_middleware=False,  # ✅ Explicit False prevents warning
)
```

### ⚠️ Works but warns: Manual middleware without explicit False
```python
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi_blog.admin import add_admin_to_app

app = FastAPI()

# Add middleware manually
app.add_middleware(SessionMiddleware, secret_key="my-key")

# Forgot to set add_session_middleware=False
add_admin_to_app(app)  # ⚠️ Warning issued, but no duplicate added

# Output:
# UserWarning: SessionMiddleware is already added to the application.
# Set add_session_middleware=False to avoid duplication.
# Skipping duplicate middleware addition.
```

## API Reference

### Parameters

**add_session_middleware: bool = True**

Controls whether `SessionMiddleware` should be added to the application.

- `True` (default): Add `SessionMiddleware` if not already present
- `False`: Do not add `SessionMiddleware` (user manages it manually)

### When to Use add_session_middleware=False

Set `add_session_middleware=False` when:

1. You've already added `SessionMiddleware` manually
2. You're using a custom session middleware
3. You need specific middleware configuration (cookie settings, etc.)
4. You're calling `add_admin_to_app()` multiple times

## Testing

Added comprehensive tests in `tests/test_session_middleware_duplication.py`:

- `test_no_duplication_when_not_added_manually()` - Normal case
- `test_warning_when_middleware_already_added()` - Duplicate detection
- `test_explicit_false_no_warning()` - Correct usage with False
- `test_multiple_calls_with_false()` - Multiple admin instances

## Migration Guide

If you see the warning:

```
UserWarning: SessionMiddleware is already added to the application.
Set add_session_middleware=False to avoid duplication.
```

**Action**: Add `add_session_middleware=False` to your `add_admin_to_app()` call:

```python
# Before (warning issued)
add_admin_to_app(app)

# After (no warning)
add_admin_to_app(app, add_session_middleware=False)
```

## Related Examples

See these examples for correct usage:

- `tests/examples/quickstart.py` - Default behavior (auto-add middleware)
- `tests/examples/api_optional.py` - Manual middleware with explicit False
- `tests/examples/admin_i18n.py` - Default behavior
- `tests/examples/admin_full_featured.py` - Default behavior

## Benefits

1. **Prevents Silent Bugs**: Duplicate middleware can cause session issues
2. **Clear Guidance**: Users get explicit warning with fix instructions
3. **Backwards Compatible**: Old code still works, just with helpful warning
4. **Defensive Programming**: Protects against common mistake
5. **Better DX**: Improves developer experience with clear messaging

## Technical Details

### How Detection Works

```python
def _has_session_middleware(app: FastAPI) -> bool:
    """Check if SessionMiddleware is already added."""
    for middleware in app.user_middleware:
        if middleware.cls == SessionMiddleware:
            return True
    return False
```

The function iterates through `app.user_middleware` and checks if any middleware's
class is `SessionMiddleware`. This works because FastAPI/Starlette store middleware
configurations in the `user_middleware` list before building the middleware stack.

### Why Warning Instead of Error?

- **Backwards Compatible**: Existing code continues to work
- **Informative**: Users learn about the issue without breaking their app
- **Graceful**: Skips duplicate addition instead of failing
- **Discoverable**: Warning appears in logs during development

### Future Considerations

In version 1.0.0, we might:
- Change default to `add_session_middleware=False`
- Require explicit True/False
- Add more sophisticated middleware detection

## Changelog Entry

This fix is documented in `changelog.md` under version 0.8.1:

```markdown
### Bug Fixes

* **Session Middleware Duplication**: Added automatic detection [#bugfix]
  - Detects if SessionMiddleware is already added
  - Issues UserWarning with clear guidance
  - Skips duplicate addition automatically
  - Backwards compatible with existing code
```
