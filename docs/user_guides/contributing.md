# Contributing to `blext`
## How do I...
**Get Started**?
```bash
# Install uv.

# Clone the Repository
git clone URL
cd blext

# Install pre-commit hooks
uvx pre-commit install

# That's it! Change some code!
```

**Test some Local Changes**?
```bash
# Run the Local 'blext'
## - Add any CLI options you want!
uv run blext
```

**Make a Commit**?
```bash
# Stage Files for the Commit
## - Generally, make sure that "one commit is one change".
git add ...  ## 'git add -A' works too, due to thorough .gitignores.

# Use 'commitizen' for Semantic Commits
## - Commit messages **are** CHANGELOG messages, and can also ref/close issues.
## - So make them good! `cz c` makes that easy.
uv run cz c  ## 'git commit' always works, but is less convenient.

# When pre-commit Makes Changes
## - For example, adding a license header or reformatting something.
## - Just re-stage and re-commit - `cz c` will remember the commit message.
git add ...  ## 'git add -A' works too, due to thorough .gitignores.
uv run cz c
```

## Overview of Tools
Development of `blext` relies on the following tools:

- `uv`: Package and project manager. **Required**.
- `pre-commit`: Enforces conventions at commit-time. **Strongly suggested**.
- `commitizen`: Commit and release manager. **Enforced** by `pre-commit`.
- `ruff fmt`: Deterministic code formatter. **Enforced** by `pre-commit`.
- `ruff lint`: Code linter. **Not enforced** (planned).
- `mypy`: Static type analysis. **Not enforced** (planned).

## Making Commits
Commits are subject to `pre-commit` hooks, if installed.
To set this up, simply run:
```bash
uvx pre-commit install
```
Then, all pre-commit hooks will run after each commit.

Sometimes it's nice to run all of the `pre-commit` hooks manually:
```bash
uvx pre-commit run --all-files
```
