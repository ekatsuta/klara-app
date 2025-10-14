# Test Database Setup

This directory contains tests for the Klara backend application.

## Setup

**No setup required!** The tests use SQLite which creates the database automatically.

### Run Tests

```bash
pytest tests/test_categorization.py -v
```

## How It Works

- `conftest.py` contains pytest fixtures that:
  - Create a SQLite test database (automatically created at `tests/test_database.db`)
  - Set up all tables before each test
  - Clean up all tables after each test (database persists but tables are dropped)
  - Create a `test_user` fixture with email `test@example.com`
  - Provide a `client` fixture for making API requests

- Each test runs in isolation with a clean database state
- The test database uses SQLite (while production uses PostgreSQL, the schema is compatible)

## Fixtures Available

- `test_db_engine`: SQLAlchemy engine for the test database
- `test_db_session`: Database session for the test
- `client`: FastAPI TestClient with test database
- `test_user`: A pre-created test user (id=1, email=test@example.com)

## Example Test

```python
def test_example(client, test_user):
    response = client.post(
        "/brain-dumps/",
        json={
            "text": "Buy milk",
            "user_id": test_user.id  # or simply 1
        }
    )
    assert response.status_code == 200
```
