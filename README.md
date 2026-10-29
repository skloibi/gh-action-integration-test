# GitHub Action Integration Test

[![status](https://github.com/skloibi/gh-action-integration-test/actions/workflows/ci.yml/badge.svg)](https://github.com/skloibi/gh-action-integration-test/actions/workflows/ci.yml)

A simple framework for designing integration tests ("scenarios") for GitHub Action definitions.

## Development

This project is managed using `uv` ([docs.astral.sh/uv](https://docs.astral.sh/uv/)).

### Update Dependencies

Use this command to update `uv.lock` based on the listed dependencies in `pyproject.toml`:

```bash
uv lock
```

Use this command to sync your local environment with the declarations in `uv.lock` and add/update the virtual environment:

```bash
uv sync --all-groups
```

### Pre-Commit Checks

This repository uses [pre-commit](https://pre-commit.com/) to automatically check and format files before each commit.

#### Setup

1. **Install `pre-commit`** (is part of dev-dependencies):

   ```bash
   uv add --group dev pre-commit
   ```

2. **Install hooks**

   ```bash
   pre-commit install
   ```

3. (optionally) **Run on all files**
   ```bash
   pre-commit run --all-files
   ```
