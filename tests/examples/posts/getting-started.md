---
title: Getting Started with FastAPI Blog
date: 2024-01-20T14:30:00
tags: [tutorial, guide, fastapi, python]
published: true
description: A comprehensive guide to setting up your first blog
---

# Getting Started

This guide will help you set up your first blog with FastAPI Blog.

## Installation

```bash
pip install fastapi-blog
```

## Quick Setup

```python
from fastapi import FastAPI
import fastapi_blog

app = FastAPI()
fastapi_blog.add_blog_to_fastapi(app)
fastapi_blog.add_admin_to_app(app)
```

That's it! Your blog is ready.
