# `blext`
_NOTE: This software should be considered alpha aka. **unstable**. It is not ready for production use. The feature-set is incomplete. The documentation is still very sparse._

_With that said, we already find it **quite useful**. We hope you'll consider sharing your experiences with us, good and bad - for example, in the Discussions / Issues sections!_

A project manager for [Blender](https://www.blender.org/) extensions, facilitating rapid and reliable development.



## Features
- **All You Need is `uv`**: The absolute only prerequisite is [`uv`](https://docs.astral.sh/uv/getting-started/installation/) and `blender`.
	_Another opinionated Python packager?_ Trust me, it's great.
- **Intuitive and Fast**: `uvx blext dev` runs Blender with your extension.
	If you only changed some code, it runs nearly instantly!
- **Effortless Deps**: Need a Python package for your addon?
	Just `uv add <pkgname>`.
	The next time you run `blext dev`, your package will be available from your extension code.
- **Single Source of Truth**: Manage your Blender extension entirely from `pyproject.toml`, using the new table `[tool.blext]`.
	`blext` is explicit about any mistakes you might make, and for your trouble, generates a correct `blender_manifest.toml` when making the addon.
- **Extension Analysis**: "Look inside" your extension with ease.
	Need to check the generated `blender_manifest.toml`?
	Re-run Blender's own extension validation?
	Or just check a platform-specific deduction?
	Just use `blext show`!

## Running `blext`
If you have `uv`, just run:
```bash
uvx blext
```

This relies on [`uv` tools](https://docs.astral.sh/uv/concepts/tools/), which is similar to `pipx`.

This is the recommended way of using `blext`.

## Using `blext`
For now, see `examples/simple` in this repository for an example of a working Blender extension.

Particular attention should be paid to the `[tool.blext]` section of `pyproject.toml`.

More in-depth documentation TBD.

## Installing `blext`
Apart from `uvx`, installation can be one more or less as with any Python package:

- `pip install --user blext`: The standard `pip` package manager should work fine. _It is strongly suggested to use a venv._
- `uv tool install blext`: This allows running `blext` without prepending `uvx blext`.
- `uv add --dev blext`: This enables running `uv run blext` from any other `uv` project.
- **Install from Source**: See the `Contributing` section.

## Documentation
For now, run `blext` alone, or run `blext --help` explicitly.

Subcommands also have help text available.
For example, `blext dev --help`.

More documentation TBD



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
