# Features
- 🛠 **Code Transforms**: `blext` provides automatic transforms on your code, to make it easier.
	- **Absolute Imports**: By default, you can't use absolute imports in Blender extensions. In `blext`, you'll find that this "magically" works! In fact, all _absolute_ imports to your own extension are cleanly and reliably replaced with equivalent _relative_ imports.
- 📦 **Fearless Dependencies**: `blext` takes care of the hassle in the background.
	- **Cross Platform**: Using [`uv`'s universal resolution](https://docs.astral.sh/uv/concepts/resolution/#universal-resolution) and custom logic, `blext` selects the most compact, compatbile wheels to ship, so that your extension works with all the platforms you wish to support.
	- **Smart Download**: `blext` downloads wheels on many threads, to maximize bandwidth utilization. `blext` also validates wheels by-hash, and caches wheels to make sure you don't have to download the same wheel twice.

- 🗂️ **Flexible Configuration**: `blext` extensions are configured just like any other Python project: With a standard `[tool]` table.
	- **PEP 621 (`pyproject.toml`)**: All Python projects have a `pyproject.toml` these days, with fields like `project.name`. `blext` uses these standard fields to configure your extension, and adds a `[tool.blext]` for configuration specific to Blender extension.
	- **PEP 723 (inline script metadata)**: `blext` supports _single-file script that build to Blender extensions_. Whatever you'd put in `pyproject.toml`, just put it in "[inline script metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata)"!
