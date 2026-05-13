# Date Handling Inconsistency Issue

## Problem Description

There is an inconsistency in how dates are handled across different modules in the codebase, leading to potential bugs with sorting and data validation.

## Identified Issues

### Issue 1: Type Inconsistency

**models.py** defines date as a simple string:
```python
date: str = Field(min_length=1)
```

**markdown_model.py** uses datetime objects:
```python
self.date = date or datetime.now()
```

**helpers.py** sorts dates as strings:
```python
posts.sort(key=lambda x: x["date"], reverse=True)
```

### Issue 2: Incorrect String Sorting

Lexicographic sorting doesn't work correctly for mixed date formats:

```python
dates = [
    "2024-01-20",              # Date only
    "2024-02-01T09:15:00",     # Full datetime
]

# After sorting (reverse=True):
# "2024-02-01T09:15:00" comes BEFORE "2024-01-20" 
# This is wrong! Feb 1 should be after Jan 20
```

**Proof**:
```python
>>> "2024-02-01T09:15:00" > "2024-01-20"
True  # String comparison, not date comparison!
```

### Issue 3: Inconsistent Date Formats in Files

Found different formats in actual markdown files:

1. `"2023-01-19T22:20:50.52Z"` - ISO with Z (UTC)
2. `2024-02-01T09:15:00` - ISO without quotes
3. `"2016-05-28"` - Date only (YYYY-MM-DD)
4. `"2024-01-20"` - Date only

### Issue 4: datetime.fromisoformat() Doesn't Support 'Z'

```python
datetime.fromisoformat("2023-01-19T22:20:50.52Z")  # ValueError!
```

The 'Z' suffix (UTC indicator) is not supported by Python's `fromisoformat()`.

### Issue 5: Dangerous Fallback in markdown_model.py

```python
except ValueError:
    date = datetime.now()  # Silently replaces invalid date with current time!
```

This is dangerous because:
- Invalid dates are silently accepted
- Original date information is lost
- No error is raised to alert the user

## Impact

**Severity**: MEDIUM

- ✅ Works for most cases (consistent ISO 8601 format)
- ❌ Fails with mixed date formats
- ❌ Silent data loss with invalid dates
- ❌ Incorrect sorting in some cases
- ❌ No validation in Pydantic models

## Real-World Example

If you have these posts:
- Post A: `date: "2024-01-20"`
- Post B: `date: "2024-02-01T09:15:00"`

String sorting will put Post B **before** Post A, even though February comes after January!

## Reproduction

```python
# Create test posts
posts = [
    {"title": "Post A", "date": "2024-01-20"},
    {"title": "Post B", "date": "2024-02-01T09:15:00"},
]

# Sort by date (current implementation)
posts.sort(key=lambda x: x["date"], reverse=True)

# Result: Post B comes first (WRONG!)
print(posts)
# [{'title': 'Post B', ...}, {'title': 'Post A', ...}]
```

## Recommended Solutions

### Solution 1: Add Date Validation in Pydantic Models

```python
from datetime import datetime
from pydantic import field_validator

class StrictFrontmatter(BaseModel):
    date: str = Field(min_length=1)
    
    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date is in ISO 8601 format."""
        try:
            # Handle 'Z' suffix
            date_str = v.replace('Z', '+00:00') if v.endswith('Z') else v
            datetime.fromisoformat(date_str)
            return v
        except ValueError:
            raise ValueError(
                f"Date must be in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS), "
                f"got: {v}"
            )
```

### Solution 2: Fix Date Parsing in markdown_model.py

```python
elif isinstance(date_value, str):
    try:
        # Handle 'Z' suffix
        date_str = date_value.replace('Z', '+00:00') if date_value.endswith('Z') else date_value
        date = datetime.fromisoformat(date_str)
    except ValueError as e:
        # Don't use fallback! Raise error instead
        raise ValueError(
            f"Invalid date format: {date_value}. "
            f"Expected ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
        ) from e
```

### Solution 3: Add Safe Date Parser in helpers.py

```python
from datetime import datetime

def parse_date_safe(date_value: str | datetime) -> datetime:
    """Parse date string to datetime, handling various formats.
    
    Args:
        date_value: Date as string or datetime object
        
    Returns:
        datetime object
        
    Raises:
        ValueError: If date format is invalid
    """
    if isinstance(date_value, datetime):
        return date_value
    
    if not isinstance(date_value, str):
        raise ValueError(f"Date must be string or datetime, got: {type(date_value)}")
    
    # Handle 'Z' suffix
    date_str = date_value.replace('Z', '+00:00') if date_value.endswith('Z') else date_value
    
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        # Try date-only format
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(
                f"Cannot parse date: {date_value}. "
                f"Expected ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            ) from e

# Use in sorting:
posts.sort(key=lambda x: parse_date_safe(x["date"]), reverse=True)
```

### Solution 4: Standardize Date Format

Choose ONE standard format and enforce it everywhere:

**Option A**: Full ISO 8601 with timezone
```yaml
date: "2024-01-20T12:00:00+00:00"
```

**Option B**: Date only (simpler)
```yaml
date: "2024-01-20"
```

**Recommendation**: Use **full ISO 8601** for precision and timezone awareness.

## Migration Plan

1. Add validation to `models.py` (non-breaking, just warns)
2. Update `helpers.py` to use proper date parsing
3. Fix `markdown_model.py` to raise errors instead of silent fallbacks
4. Add tests for mixed date formats
5. Document the required date format in README
6. (Optional) Add migration script to normalize existing dates

## Testing

Add tests to verify:

```python
def test_date_sorting_mixed_formats():
    """Test that dates are sorted correctly regardless of format."""
    posts = [
        {"date": "2024-01-20", "title": "A"},
        {"date": "2024-02-01T09:15:00", "title": "B"},
        {"date": "2023-12-15", "title": "C"},
    ]
    
    sorted_posts = sort_posts_by_date(posts)
    
    # Should be: B (Feb), A (Jan), C (Dec)
    assert sorted_posts[0]["title"] == "B"
    assert sorted_posts[1]["title"] == "A"
    assert sorted_posts[2]["title"] == "C"

def test_invalid_date_raises_error():
    """Test that invalid dates raise clear errors."""
    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date("not-a-date")
```

## Related Files

- `src/fastapi_blog/models.py` - Date field definition
- `src/fastapi_blog/helpers.py` - Date sorting
- `src/fastapi_blog/admin/markdown_model.py` - Date parsing
- `src/fastapi_blog/admin/markdown_crud.py` - Date display

## Status

**CONFIRMED** - Issue exists and affects sorting and validation

## Priority

**MEDIUM** - Works in most cases but can cause subtle bugs

## Next Steps

1. Add this to backlog for version 0.9.0
2. Create tests to verify the issue
3. Implement fixes one by one
4. Update documentation with required date format
