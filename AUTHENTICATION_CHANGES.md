# Authentication Changes in editor.py

## Problem (Before)

The `require_authentication()` function in `editor.py` tried to import from `backend.auth.*`:

```python
from backend.auth.config import SECRET_KEY, ALGORITHM
from backend.auth.models import User
```

**Issues:**
- ❌ Import from non-existent module (when fastapi-blog is used standalone)
- ❌ Broke package autonomy
- ❌ JWT auth never worked in practice
- ❌ Tests passed WITHOUT authentication (didn't use `require_authentication`)

## Solution (After)

### 1. Removed JWT logic from `editor.py`

```python
async def require_authentication(request: Request) -> dict:
    """Require authentication via session cookie.
    
    This function is part of fastapi-blog and only checks session-based
    authentication (starlette-admin SessionMiddleware).
    
    For JWT authentication, the parent application should override this
    dependency or add custom middleware.
    """
    # Check session cookie (set by starlette-admin or SessionMiddleware)
    user = request.session.get('user')
    if user:
        return {
            'username': user,
            'is_admin': request.session.get('is_admin', False)
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Authentication required. Please login via admin panel.',
        headers={'WWW-Authenticate': 'Session'},
    )
```

### 2. Added `require_auth` parameter

```python
def add_editor_to_app(
    app: FastAPI,
    prefix: str = "/api/posts",
    posts_dirname: str = "posts",
    strict: bool = True,
    ui: bool = True,
    ui_prefix: str = "/admin/editor",
    require_auth: bool = True,  # NEW PARAMETER
) -> FastAPI:
```

**Usage:**
- `require_auth=True` (default): Use session authentication
- `require_auth=False`: Disable authentication (for tests or public access)

### 3. Updated tests

```python
# Tests now explicitly disable auth
app = add_editor_to_app(app, require_auth=False)
```

## Architecture Philosophy

✅ **JWT Authentication** (`backend/auth/`) - External to fastapi-blog, for frontend only  
✅ **fastapi-blog** - Autonomous package, no dependency on `backend/auth`  
✅ **Session Authentication** - Built into fastapi-blog via starlette-admin  
✅ **Editor API** - Uses only session auth (from starlette-admin)

## Integration Example

### Parent application can add JWT auth via middleware:

```python
from fastapi import FastAPI
from fastapi_blog import add_editor_to_app

app = FastAPI()

# Add session middleware for admin panel
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="...")

# Add admin panel (provides session auth)
from fastapi_blog import add_admin_to_app
add_admin_to_app(app, base_url='/dashboard')

# Add editor API (uses session auth from admin)
add_editor_to_app(app, ui=False)

# JWT auth is handled separately in parent app
# (e.g., via custom middleware or route guards)
```

## Benefits

1. ✅ **Package autonomy**: fastapi-blog works standalone
2. ✅ **No broken imports**: All dependencies are internal
3. ✅ **Clear separation**: JWT for frontend, sessions for admin
4. ✅ **Tests work**: Can disable auth when needed
5. ✅ **Flexibility**: Parent app can add custom auth logic

## Migration Notes

- ✅ No breaking changes for existing installations
- ✅ Default behavior unchanged (`require_auth=True`)
- ✅ Tests updated to use `require_auth=False`
- ✅ Session auth still works as before
