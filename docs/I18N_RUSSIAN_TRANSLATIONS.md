# Russian Translations for Admin Panel

## Overview

FastAPI Blog now includes comprehensive Russian translations for the admin panel interface. The internationalization system uses starlette-admin's built-in i18n support combined with custom translations for project-specific elements.

## Features

### ✅ What Works

1. **Built-in Interface Elements** (from starlette-admin):
   - Login form: "Войти в свой аккаунт", "Имя пользователя", "Пароль"
   - Table controls: "Экспорт", "Видимость столбцов", "Конструктор поиска"
   - Pagination: "Показать X строк", "Записи с X до Y из Z записей"
   - Common actions: "Сохранить", "Удалить", "Отменить"
   - Messages: "Записи отсутствуют", "Первая", "Последняя"

2. **Custom Labels** (project-specific):
   - Navigation menu: "Главная", "Пользователи", "Посты"
   - Breadcrumbs and page titles

3. **Language Switcher**:
   - Dropdown in top navigation bar
   - Auto-reload on language change (via JavaScript)
   - Cookie-based language persistence

## Configuration

### Basic Setup (Russian by Default)

\`\`\`python
from fastapi import FastAPI
import fastapi_blog

app = FastAPI()

# Add blog with Russian admin panel
fastapi_blog.add_admin_to_app(
    app,
    title="Админ-панель блога",  # Russian title
    i18n_enabled=True,
    i18n_default_locale="ru",  # Default to Russian
    i18n_locales=["en", "ru"],  # Available languages
)
\`\`\`

### English by Default

\`\`\`python
fastapi_blog.add_admin_to_app(
    app,
    title="Blog Admin Panel",
    i18n_default_locale="en",  # Default to English
    i18n_locales=["en", "ru"],
)
\`\`\`

### Single Language (No Switcher)

\`\`\`python
# Russian only
fastapi_blog.add_admin_to_app(
    app,
    i18n_locales=["ru"],  # No switcher, only Russian
)

# English only
fastapi_blog.add_admin_to_app(
    app,
    i18n_locales=["en"],  # No switcher, only English
)
\`\`\`

## How It Works

### Translation Architecture

1. **starlette-admin translations**: Built-in translations for common UI elements (buttons, forms, tables)
2. **Custom translations**: Project-specific labels set during admin initialization

### Label Selection Logic

Custom labels (menu items, view names) are selected based on \`i18n_default_locale\`:

\`\`\`python
# In add_admin_to_app()
home_label = "Главная" if i18n_default_locale == "ru" else "Home"
users_label = "Пользователи" if i18n_default_locale == "ru" else "Users"
posts_label = "Посты" if i18n_default_locale == "ru" else "Posts"
\`\`\`

### Language Persistence

- Language preference stored in \`language\` cookie
- Cookie set by JavaScript on language switcher click
- Page automatically reloads to apply new language
- Session persists across page reloads

## Translation Files

Translation files are located in \`src/fastapi_blog/translations/\`:

\`\`\`
src/fastapi_blog/translations/
├── en/
│   └── LC_MESSAGES/
│       ├── admin.po  # English translations
│       └── admin.mo  # Compiled translations
└── ru/
    └── LC_MESSAGES/
        ├── admin.po  # Russian translations
        └── admin.mo  # Compiled translations
\`\`\`

### Compiling Translations

If you modify .po files, recompile with msgfmt:

\`\`\`bash
msgfmt src/fastapi_blog/translations/ru/LC_MESSAGES/admin.po \
       -o src/fastapi_blog/translations/ru/LC_MESSAGES/admin.mo

msgfmt src/fastapi_blog/translations/en/LC_MESSAGES/admin.po \
       -o src/fastapi_blog/translations/en/LC_MESSAGES/admin.mo
\`\`\`

## Limitations

### Static vs Dynamic Labels

**Current behavior**: Custom labels (menu items) are set once during admin initialization based on \`i18n_default_locale\`. They do NOT change dynamically when user switches language.

**Example**:
- If \`i18n_default_locale="ru"\`, menu shows: "Главная", "Пользователи", "Посты"
- User switches to English → menu labels stay in Russian
- But built-in UI elements (buttons, forms) change to English

**Workaround**: Set \`i18n_default_locale\` to match your primary audience's language.

### Why This Limitation?

starlette-admin's ModelView.label is a class attribute, not a dynamic property. It's evaluated once during view creation, not on each request.

**Future improvement**: We could implement dynamic labels by:
1. Overriding ModelView.get_label() method
2. Using lazy_gettext with proper context
3. Creating custom view wrappers

## Best Practices

### 1. Choose Default Locale Wisely

\`\`\`python
# For Russian audience
i18n_default_locale="ru"

# For international audience
i18n_default_locale="en"
\`\`\`

### 2. Include Both Languages

Unless you're targeting a single language audience, include both:

\`\`\`python
i18n_locales=["en", "ru"]  # Recommended
\`\`\`

### 3. Match Title with Locale

\`\`\`python
# Russian setup
fastapi_blog.add_admin_to_app(
    app,
    title="Админ-панель блога",
    i18n_default_locale="ru",
)

# English setup
fastapi_blog.add_admin_to_app(
    app,
    title="Blog Admin Panel",
    i18n_default_locale="en",
)
\`\`\`

## Examples

See working examples in \`tests/examples/\`:

- \`admin_i18n.py\` - Russian by default with EN/RU switcher
- \`admin_full_featured.py\` - Full featured with i18n
- \`quickstart.py\` - Simple setup

## Troubleshooting

### Menu Labels Not Translating

**Problem**: Menu shows "Home", "Users", "Posts" in English even after switching to Russian.

**Explanation**: This is expected behavior (see Limitations above). Custom labels are set during initialization.

**Solution**: Set \`i18n_default_locale="ru"\` if Russian is your primary language.

### Built-in UI Not Translating

**Problem**: Buttons, forms, tables stay in English.

**Solution**: 
1. Ensure \`starlette-admin[i18n]\` is installed: \`pip install starlette-admin[i18n]\`
2. Verify \`i18n_enabled=True\` in \`add_admin_to_app()\`
3. Check that translations exist: \`ls /path/to/starlette_admin/translations/ru/\`

### Language Switcher Not Appearing

**Problem**: No language dropdown in navigation bar.

**Solution**: Include multiple locales:
\`\`\`python
i18n_locales=["en", "ru"]  # Switcher appears
# NOT: i18n_locales=["ru"]  # No switcher (single language)
\`\`\`

## Related Documentation

- [QUICKSTART.md](../QUICKSTART.md) - Quick start guide with i18n examples
- [DATABASE.md](DATABASE.md) - Database and model translations
- starlette-admin i18n docs: https://github.com/jowilf/starlette-admin

## Changelog

### Version 0.8.1 (2026-05-13)

- ✅ Added Russian translations for all built-in UI elements
- ✅ Added Russian labels for custom views (Home, Users, Posts)
- ✅ Created translation files (admin.po/admin.mo)
- ✅ Configured i18n in \`add_admin_to_app()\`
- ⚠️ Known limitation: Custom labels are static (based on default locale)

