# Development guide

## Set up the environment

The project uses `pyproject.toml`, `uv.lock`, and Python 3.13 or newer. From the
repository root, create or refresh the environment only when `.venv` is missing
or stale:

```bash
uv sync --locked
```

Run tools directly from the project environment:

```bash
.venv/bin/definedcli --help
.venv/bin/pytest
```

## Run tests

Run the complete suite:

```bash
.venv/bin/pytest
```

Run one test module while iterating:

```bash
.venv/bin/pytest tests/test_cli_behavior.py
```

The test suite uses fakes and mocks for request behavior; it does not require a
real API key.

## Try the local CLI

The virtual environment exposes the current checkout directly:

```bash
.venv/bin/definedcli --version
.venv/bin/definedcli hosts create --help
```

Commands that call authenticated endpoints require `DEFINED_API_KEY`. The
downloads listing can be used without one:

```bash
.venv/bin/definedcli downloads list
```

## Repository layout

```text
src/defined_client/
├── client.py       HTTP session, configuration, and error mapping
├── resources.py    Low-level endpoint wrappers
├── services/       Safe updates, lookups, and pagination helpers
└── cli/            Click command groups and output handling
tests/
├── cli/             CLI contract and end-to-end workflow tests
└── client/          HTTP, resource, and service-layer tests
spec/openapi.yaml    Defined Networking OpenAPI description
```

Reusable CLI fakes and fixtures live beside the CLI tests in `tests/cli/`.

When adding an endpoint, keep its low-level behavior in a resource object. Add
a service method only when the operation composes requests or provides a safer
workflow. CLI commands should preserve the standard API envelope in JSON mode,
write errors only to stderr, and keep credentials out of diagnostics.

## Build the package

```bash
uv build
```

The resulting distributions are written to `dist/`.
