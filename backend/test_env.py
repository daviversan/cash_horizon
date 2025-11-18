# test_env.py
import os
from app.config import settings

print("=" * 50)
print("Environment Configuration Check")
print("=" * 50)

checks = [
    ("Gemini API Key", bool(settings.gemini_api_key)),
    ("Search API Key", bool(settings.google_search_api_key)),
    ("Search Engine ID", bool(settings.google_search_engine_id)),
    ("Search Enabled", settings.google_search_enabled),
    ("Secret Key", bool(settings.secret_key)),
]

for name, value in checks:
    status = "✅" if value else "❌"
    print(f"{status} {name}: {value}")

print("=" * 50)