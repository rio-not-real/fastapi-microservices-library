# AGENTS.md

This file governs the whole `fastapi-microservices-library` repository.

## How I Work Here

I work from the repository root unless a task explicitly targets another path.
I use `rg` for text and file searches. I keep edits scoped to the `src/fml`
library code, tests, scripts, or packaging files needed for the task.

I treat this as a small typed Python library for FastAPI and Starlette. I keep
runtime dependencies minimal, and I prefer optional extras for functionality
that is not required by the core package. I preserve the `src` layout, the
`fml.py.typed` marker, and compatibility with Python `>=3.11,<3.15`.

I follow the existing style: Pydantic v2 models, Starlette/FastAPI primitives,
Ruff formatting with 88 character lines, double quotes, and explicit type hints
on public behavior. I avoid broad framework abstractions unless they clearly
reduce repeated setup for library users.

## Package Behavior

I keep public behavior predictable for API consumers:

- Problem detail responses follow RFC 9457 and use
  `application/problem+json`.
- Custom exceptions in `src/fml/errors.py` map cleanly to HTTP status codes.
- Middleware keeps request metadata such as `X-Request-ID` stable across the
  request and response.
- I keep serialization changes in `src/fml/responses.py` compatible with
  Pydantic models and normal JSON-compatible content.
- I keep shared models in `src/fml/models.py` small, reusable, and documented
  through Pydantic field metadata when useful.

When I change public API behavior, I update or add tests under `tests/` and
consider whether the README needs a usage example.

## Commands I Run

I install or refresh the development environment with:

```bash
uv sync --locked --all-extras --dev
```

I run the full test suite with:

```bash
uv run pytest
```

I run the same lint/type checks used by CI with:

```bash
uv run bash scripts/lint.sh
```

I format code with:

```bash
uv run bash scripts/format.sh
```

For focused validation, I run the narrowest relevant pytest target first, such
as:

```bash
uv run pytest tests/exceptions_test.py
```

Before finishing a code change, I run the relevant focused tests and then the
full lint command unless the task is documentation-only.

## Git And Safety

I check `git status --short` before making edits and before summarizing work.
I do not revert user changes or rewrite history unless explicitly asked. I ask
before destructive operations such as deleting files outside the requested
scope, force-resetting git state, or changing release metadata.

I keep generated artifacts, caches, and virtual environments out of commits.
The repo already ignores common local state such as `.venv`, `.pytest_cache`,
`.ruff_cache`, build outputs, and coverage files.

## Completion Checklist

Before I finish, I confirm:

- the changed files match the requested scope
- tests cover behavior changes
- `uv run bash scripts/lint.sh` passes when code changed
- public API or packaging changes are reflected in docs when needed
- `git status --short` only shows intended changes
