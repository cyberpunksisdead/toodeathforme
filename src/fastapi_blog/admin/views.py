"""Custom ModelView classes for admin models."""

from starlette_admin.contrib.sqla import ModelView

class UserModelView(ModelView):
  """Custom view for User model with password handling."""
  exclude_fields_from_list = ['hashed_password']
  exclude_fields_from_detail = ['hashed_password']
  exclude_fields_from_edit = ['hashed_password', 'created_at', 'updated_at']
  exclude_fields_from_create = ['created_at', 'updated_at']
  
  # Note: In production, add password hashing logic in before_create/before_edit hooks

class PostModelView(ModelView):
  """Custom view for Post model."""
  exclude_fields_from_edit = ['created_at', 'updated_at']
  exclude_fields_from_create = ['created_at', 'updated_at']
  
  # Make content field use textarea
  form_overrides = {
    'content': {'widget': 'textarea', 'rows': 20},
    'description': {'widget': 'textarea', 'rows': 3},
  }
