# Tracker Core

Shared library for Free LLM API Tracker and AI/Tech News Tracker.

## Structure

```
tracker-core/
├── pyproject.toml
├── requirements.txt
├── .env.example
├── src/
│   └── tracker_core/
│       ├── __init__.py
│       ├── schema.py          # Pydantic models, versioned
│       ├── adapters/          # Per-source adapters
│       │   ├── __init__.py
│       │   ├── base.py        # Adapter interface
│       │   └── github.py
│       ├── pipeline/          # Stage modules
│       │   ├── __init__.py
│       │   ├── fetcher.py
│       │   ├── parser.py
│       │   ├── deduplicator.py
│       │   ├── store.py
│       │   ├── reporter.py
│       │   └── notifier.py
│       ├── scheduler.py       # APScheduler wrapper
│       ├── cache.py           # File-based cache
│       └── config.py          # YAML config loader
├── tests/
│   ├── conftest.py
│   ├── test_schema.py
│   ├── test_adapters.py
│   ├── test_pipeline.py
│   └── test_scheduler.py
└── schedule.yaml              # Cron/interval config
```

## Adapter Interface

```python
class BaseAdapter(Protocol):
    def fetch(self) -> RawData: ...
    def parse(self, raw: RawData) -> list[Item]: ...
    def to_schema(self, item: Item) -> dict[str, Any]: ...
```

## Schema Versioning

- All models in `schema.py`
- New fields: optional with defaults
- Breaking changes: new version class, migration script
