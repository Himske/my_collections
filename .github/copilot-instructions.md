# Project guidance

- This is a Python 3.13+ FastAPI application managed with `uv`. Run project commands from the repository root:
  - `uv sync` to install dependencies.
  - `uv run python db.py` to create missing SQLite tables.
  - `uv run uvicorn main:app --reload` to run the application.
- The SQLite URL in `db.py` is relative to the current working directory. Keep commands that access the application database rooted at the repository; otherwise they may open or create a different `database.db`.
- Keep API routes in `routers.py` and their SQLModel tables and request/response models in `models.py`. When changing API fields or behavior, update the corresponding client code under `static/` so its fetch requests and JSON handling remain consistent.
- The UI is plain HTML, CSS, and JavaScript in `static/`, served by `main.py` under `/static/`; keep page routes and static asset paths consistent with that setup.
- Book lookup and cover downloads are handled by `book_find.py` through the external Nicebooks site. Keep network-dependent scraping there, and preserve the cover files and paths expected under `static/book_covers/`. Do not assume lookups work without an internet connection.
- Run the test suite from the repository root with `uv run pytest`. Put pytest tests in `tests/` and use pytest's `test_*.py` naming convention.
- Run Ruff from the repository root with `uv run ruff check .`. Its enabled rules and line length are configured in `pyproject.toml`.
- API tests should use FastAPI's `TestClient` and an isolated test database or overridden session dependency; never let tests write to the real `database.db`. Keep tests independent of the external Nicebooks service by mocking the network-facing lookup when needed.
