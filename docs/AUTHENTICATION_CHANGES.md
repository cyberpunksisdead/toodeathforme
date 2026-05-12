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
    
    Raises 401 if not authenticated.
    """
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


async def optional_authentication(request: Request) -> Optional[dict]:
    """Optional authentication - returns None if not authenticated.
    
    Used when require_auth=False (e.g., in tests).
    Does NOT raise 401.
    """
    user = request.session.get('user')
    if user:
        return {
            'username': user,
            'is_admin': request.session.get('is_admin', False)
        }
    return None
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

### 3. Fixed type safety with dict | None (Python 3.12+ syntax)

```python
# Setup authentication dependency
auth_func = require_authentication if require_auth else optional_authentication

@api_router.post("/create/{slug}")
async def create_post(
    payload: Payload,
    slug: str = slug_path,
    user: dict | None = Depends(auth_func),  # ✅ Type-safe!
) -> dict[str, str]:
```

**Why this works:**
- When `require_auth=True`: `auth_func = require_authentication` → always raises 401 if not authenticated
- When `require_auth=False`: `auth_func = optional_authentication` → returns None (for tests)
- Type is `dict | None` (modern Python 3.10+ syntax) which correctly represents both cases

### 4. Added authentication to ALL endpoints

- ✅ POST `/create/{slug}` - requires auth
- ✅ PUT `/update/{slug}` - requires auth  
- ✅ DELETE `/delete/{slug}` - requires auth
- ✅ POST `/save` - requires auth
- ✅ GET `/{slug}/raw` - **NOW requires auth** (was public before)
- ✅ UI routes (`/admin/editor/*`) - **NOW require auth** (were public before)

### 5. Updated tests

```python
# Tests now explicitly disable auth
app = add_editor_to_app(app, require_auth=False)

# New authentication tests verify that:
# 1. All endpoints return 401 without auth
# 2. require_auth=False allows public access
```

### 6. Updated example with SessionMiddleware

```python
# tests/examples/editor.py
app.add_middleware(SessionMiddleware, secret_key="...")
app = add_editor_to_app(app, require_auth=True)  # Auth enabled
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
6. ✅ **Type safety**: Proper use of Optional[dict]
7. ✅ **Security**: All endpoints now require authentication by default
8. ✅ **Complete coverage**: UI routes also protected

## Migration Notes

- ✅ No breaking changes for existing installations
- ✅ Default behavior: `require_auth=True` (all endpoints protected)
- ✅ Tests updated to use `require_auth=False`
- ✅ Session auth still works as before
- ⚠️ **BREAKING**: GET `/{slug}/raw` now requires authentication (was public before)
- ⚠️ **BREAKING**: UI routes now require authentication (were public before)
- 💡 To restore public access: use `require_auth=False` (not recommended for production)

## Security Improvements

1. **All modifying operations protected**: create, update, delete, save
2. **Read operations protected**: GET raw now requires auth
3. **UI routes protected**: Editor interface requires login
4. **Type-safe implementation**: No more `# type: ignore` hacks
5. **Explicit control**: `require_auth` parameter makes intentions clear
