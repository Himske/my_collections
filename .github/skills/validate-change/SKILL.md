---
name: validate-change
description: "Inspect and validate a code change in this repository. Use after implementing or reviewing changes to choose and run relevant pytest tests and available lint checks, then report what passed, failed, or was not run."
---

# Validate a Change

Inspect the current change, select focused checks that cover it, run the applicable checks, and report their exact outcomes. Do not change application code or dependencies as part of validation.

## Procedure

1. Inspect the worktree and the change diff. Identify changed files and the behavior they affect; do not attribute unrelated pre-existing changes to this change.
2. From the repository root, find relevant tests under `tests/` or alongside the changed code. Run the narrowest applicable tests with `uv run pytest <test-file-or-directory>`. If the change is broad or no narrower selection is reliable, run `uv run pytest`.
3. If there are no applicable tests, do not report a successful test run. Mark tests as **not run** and say no relevant tests were found.
4. For changed Python files, run Ruff with `uv run ruff check <changed-python-files>`. Ruff is a project dependency, and its rules are configured in `pyproject.toml`. If Ruff cannot be run, mark lint as **not run** and explain why. There is no configured linter for the static HTML, CSS, or JavaScript files; report that no lint check was available when those files change.
5. Keep checks isolated from external services and persistent data. For API tests, use a test database or overridden session dependency, and mock Nicebooks lookups. Do not run database-population or destructive maintenance commands against the application's database as validation.
6. Report each check under **Passed**, **Failed**, or **Not run**. Include the command, concise results, and any failure details. Do not describe a check that was skipped or unavailable as passing.
