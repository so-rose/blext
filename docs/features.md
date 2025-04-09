!!! abstract
	**Already convinced?** See [Getting Started](user_guides/getting_started.md)!

	**Looking for a more practical reference?** Please refer to the "User Guides". In particular, the [CLI / Commands](user_guides/cli/commands.md) reference has many examples of how to make use of `blext`'s features in practice.

# Features
A bit more depth is provided for each of the "highlights", to help illustrate what `blext` can do!



## 🛠 **Welcome to Modern Python**
`blext` extensions are standard Python projects, powered by the cutting-edge [`uv` project manager](https://docs.astral.sh/uv/) and a standard `pyproject.toml`.

- **PEP 621 (`pyproject.toml`)**: All Python projects have a `pyproject.toml` these days, with fields like `project.name`. `blext` uses these standard fields to generate `blender_manifest.toml`, adding a `[tool.blext]` for fields specific to Blender extensions.
- **PEP 723 (inline script metadata)**: `blext` supports single-file Blender extensions! Whatever you'd put in `pyproject.toml`, just put it in "[inline script metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata)", and `blext` will take care of the rest.
- **Easy Development Tools**: Development dependencies like `ruff` are never bundled into your extension. Just `uv add --dev <dep>` - now, `uv run <dep>` will invoke a locked version of `<dep>` for all developers.
- **No-`bpy`**: The `.venv` that `uv sync` creates for you is _almost_ identical to the one your extension sees inside of Blender. This makes it easy you to create a package that works with and without `bpy`, letting you de-duplicate programming work meant to work both inside and outside of Blender.
- **Your Extension Library**: `blext` is a CLI application, but it's also _just a Python library_. The CLI application is only one face of `blext`; the well-documented libraries within `blext` serve as foundational abstractions for many other kinds of software.



## 🚀 **Snappy at Scale**
Create, download, build, analyze, and run large extensions in moments, without resorting to fragile mechanisms that fracture deployment from development.

- **Smart Download**: `blext` downloads wheels on many threads, to maximize bandwidth utilization. `blext` also validates wheels by-hash, and caches wheels to make sure you don't have to download the same wheel twice.
- **Incremental Build**: The build process first "pre-packs" large binary wheels, as well as other large files of your choice. Then, whenever source code is modified, `blext` only needs to copy small `.py` files, causing re-builds that don't modify dependencies / large files to happen very quickly.
- **Only Real Installs**: `blext` only ever performs "real" installations - no hot-patching a blessed `site-packages`. Run-edit-run workflows are therefore always representative of what the user will experience - while also happening as fast as Blender can load your extension!



## 📦 **Fearless PyDeps**
"Just `uv add scipy`"! Never be scared of adding Python dependencies to your extension again - `blext` handles VFX reference platform compatibility, dependency resolution, and cross-platform wheel selection. _We also got tired of choosing wheel tags._

- **Powerful Guarantees**: `blext` enforces compatibility with the bundled PyDeps of all suppported Blender versions, by building on top of `uv`'s powerful resolver to deterministically select the best wheels to ship with your extension. 
- **End-User Compatibility**: Incorrectly selecting `glibc`/`macos` versions of wheels is a _silent compatibility killer_. `blext` is **always** explicit about this: The minimum `glibc`/`macos` version of each Blender version guides wheel selection, in order to gurantee that extensions will work wherever Blender does (defined by Blender's own minimum requirements).
- **Useful Tweaks**: When Blender's minimum `glibc`/`macos` prohibits the use of a dependency, `blext` clearly communicates how to raise the minimum required `glibc`/`macos` for your extension. Other tweaks to ex. supported Python interpreter tags are also available.
- **Self-Explanatory Errors**: When there's a problem with dependencies, `blext` will **actually explain** what's invalid/missing, why this might be the case, and even try to guide you to a solution.
- **BLVersion-Specific Dependencies**: In addition to Blender-vendored PyDeps, `blext` also lets you assign pydeps to specific Blender versions! `blext` uses this to fully traverse the `uv`-resolved dependency graph, checking environment marker validity on every edge.



## 🗂️ **Swiss-Army Knife of Extensions**
!!! warning
	From this section, the following features are **missing / work-in-progress**:
	
	- `blext init`: See [#45](https://codeberg.org/so-rose/blext/issues/45)
	- `blext check`: See [#52](https://codeberg.org/so-rose/blext/issues/52)
	- HTTP and `git` Extension Locations: See [#41](https://codeberg.org/so-rose/blext/issues/41) and [#42](https://codeberg.org/so-rose/blext/issues/42).
	- Packed Extension Source: See [#39](https://codeberg.org/so-rose/blext/issues/39).
	- `csv` from `blext deps`: See [#38](https://codeberg.org/so-rose/blext/issues/38).

	Please let us know if any of these are of particular importance to you.

`blext` is more than a build system - it's a complete suite of tools for dealing with extensions.

- **Starting Out**: The `blext init` suite of commands make it easy to generate new `blext` extensions from scratch, or from existing projects. For instance, you can generate a new `blext` extension
- **Great Extensions Can Come from Anywhere**: Any `blext` command that takes a `<location>`, such as `blext run <location>`, can be given an extension located on your filesystem (`path/to/ext/`), on a website (`http://example.org/ext.py`), or even in a remote `git` repository.
- **Insight with Integration**: The `blext show` suite of commands can help you understand your extension. For instance, you can generate `blender_manifest.toml` as `json`, print the current global config as `toml`, or export the extension's wheel selecton to a `csv` file!
- **Your Fixer-Upper Companion**: `blext` accepts existing extensions as a `<location>`, too! That means you can run all checks on an existing extension using `blext check <location>`, or even directly repack it using `blext build <location>`. Since `blext` only scans the wheels to reconstruct the underlying minimal set of dependencies, such re-packing has the added bonus of very quickly detecting _and sometimes automatically fixing_ any unseen problems that the particular choice of wheels may be causing.
- **Fixed `blext` Version**: When you `uv add --dev blext` to your extension project, `blext` will automatically detect that a specific version of `blext` is used in that project, and forward its command to that version. _This guarantees that anybody building your extension will always do so using the exact same version of `blext` as everybody else - the version you pinned to your project._



## 🛠 **Code Transforms**
!!! warning
	All features in this section are **missing / work-in-progress**.

	Please see [#21](https://codeberg.org/so-rose/blext/issues/21) for the latest.

`blext` can automatically perform certain "safe" code rewrites, such as AST-level rewrite of absolute imports to relative imports.

- **Absolute Imports**: In `blext`, you'll find that absolute imports from your own extension "magically" work. `blext` parses your code, detects absolute imports to your own extension, and transparently replaces them with equivalent _relative_ imports, without affecting your code.



## 🏢 **Robust by Design**
!!! warning
	From this section, the following features are **missing / work-in-progress**:
	
	- `pytest`: See [#10](https://codeberg.org/so-rose/blext/issues/10)
	- _Documentation Quality_: The quality of the documentation is yet not where it needs to be to faithfully make the claims in this section.
	- _General Stability_: The stability of the project is not yet where it needs to be to faithfully call `blext` "robust".

	Please let us know if any of these are of particular importance to you.

We believe that great tools comes from well-chosen, well-integrated abstractions, presented concisely.

- **Immutable-First**: `blext` prioritizes immutable `pydantic` models, allowing use of memoization for transparent performance optimization.
- **Deeply Documented**: `blext` strives for a _lovingly_ documented API, to make the code easy to work with, and to make `blext` easy to use as a library.
- **Sensible Analysis Suite**: `blext` is statically typed, and fully passes `basedpyright`. `blext` also passes `ruff`, for both linting and formatting. Finally, `hypothesis` property-based testing is combined with `pytest` to provide reasonable coverage.
- **Custom Exception Hooks**: Exceptions are parsed and processed before presentation to the user, in order to enhance the agency of the user to deal with errors they may encounter.

## 🌐 **Respects your Freedoms**
`blext` preserves your freedom to use, modify, fork, redistribute, or even sell `blext`, **so long as you extend the same freedoms as you were granted** under the [AGPL](https://www.gnu.org/licenses/agpl-3.0.html) software license.

_For more details, see our [License Policy](https://docs.sofus.io/blext/stable/reference/policies/licensing.html)._
