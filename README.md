# `blext`
A fast, convenient project manager for Blender extensions.

Quite experimental for the moment.
**Documentation TBD.**

For now, install the `uv` package manager and run
```bash
uvx blext
```
to try out `blext`.
A barebones help text should be available even now.

# Contributing
## Tooling
- `uv`: Package and project manager.
- `ruff lint`: Linter. Currently not enforced.
- `ruff fmt`: Linter. Currently enforced.
- `mypy`: Static type analysis. Currently not enforced.
- `commitizen`: Commit and release conventions. Currently not enforced.
- `pre-commit`: Guarantees

## Making Commits
Commits are subject to `pre-commit` hooks.
To set this up, run:
```bash
uvx pre-commit install
```

Thereafter, it will run after each commit.

Sometimes it's nice to run all of the `pre-commit` hooks manually:

```bash
uvx pre-commit run --all-files
```

