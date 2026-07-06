# Changelog

All notable changes to CommandDesk will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **CRITICAL:** Fixed `rate_limiter.py` dict initialization typo (`=()` → `={}`) that broke rate limiting entirely
- **CRITICAL:** Added missing `import requests` to `zammad.py` — would crash on ticket operations
- **CRITICAL:** Fixed SQL injection vulnerability in `session_manager.py` — replaced string formatting with parameterized query
- **CRITICAL:** Fixed wrong Redis URLs in `health_monitor.py` and `whatsapp_webhook.py` (referenced PostgreSQL port 5432 instead of Redis port 6379)
- **CRITICAL:** Fixed `email_fetcher.py` to route email-to-ticket through existing `/chat` endpoint instead of non-existent `/tickets/create`
- Moved `import re` to module level in `whatsapp_webhook.py` (was inside function)
- Removed hardcoded placeholder password from `analytics.py` default URL
- Replaced `redis.keys()` with `SCAN` cursor iteration in `session_manager.py` and `health_monitor.py` to avoid O(N) blocking calls
- Added `.dockerignore` to prevent build context leaks
- Added `j1.yaml` for pipeline registry metadata

### Changed

- `session_manager.py`: `import uuid` moved to module level
- `health_monitor.py`: Fixed Redis URL default to proper format
- `whatsapp_webhook.py`: Fixed Redis URL default to proper format
- `analytics.py`: PostgreSQL URL default now empty (must be set via env)
