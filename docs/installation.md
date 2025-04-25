!!! abstract
	**Confused what to do?** See [Getting Started](user_guides/getting_started.md)!

	**Which installation method is best?** We _strongly suggest_ installing `blext` as a [global `uv tool`][install-wuv-tool-recommended].
	Then, into each extension project as [per-project `blext`][install-wuv-add-dev-recommended] - this is done automatically if you use `blext init`.

# Installation
In general, there are two main ways you'll want to install and use `blext`:

- [**Global**][install-wuv-tool-recommended]: Install the `blext` command for a user.
- [**Per-Project**][install-wuv-add-dev-recommended]: Install `blext` as a `uv run` command for a specific project.

!!! note
	To use the `blext` installed in a project, you would usually have to `uv run blext`.
	
	`blext` automatically does this for you.
	It will always automatically check if you're in a project with a local `blext` version installed, and forward your command to `uv run blext`.



## Standard Installation Methods
### Install w/`uv tool` (**recommended**)
**Global** method using `uv`'s "tool" interface.

!!! warning
	This installation method requires [`uv`](https://docs.astral.sh/uv/) to be correctly installed beforehand, since every `blext` project is also a `uv` project.
 
	Please refer to the [`uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/).

=== "Latest"
	```bash
	uv tool install blext
	```

=== "Nightly (`git`)"
	```bash
	uv tool install git+https://codeberg.org/so-rose/blext.git
	```



### Install w/`uv add --dev` (**recommended**)
**Per-project** method using `uv`'s dependency management

!!! warning
	This installation method requires [`uv`](https://docs.astral.sh/uv/) to be correctly installed beforehand, since every `blext` project is also a `uv` project.
 
	Please refer to the [`uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/).

!!! info
	A per-project installation of `blext` binds a specific version of `blext` to each to each extension project.
	From anywhere within your extension project, you can run `blext` commands using the project-specific version of `blext`, like this:

	```bash
	uv run blext --help  ## the 'uv run' prefix runs a project-specific command
	```

**First**, change directories to anywhere within your extension project.

=== "Linux"
	```bash
	cd $HOME/path/to/my/extension/project
	```
=== "MacOS"
	```bash
	cd $HOME/path/to/my/extension/project
	```
=== "Windows"
	```powershell
	cd $HOME\path\to\my\extension\project
	```

**Then**, install `blext`.

=== "Latest"
	```bash
	uv add --dev blext  ## --dev keeps blext out of your extension
	```

=== "Nightly (`git`)"
	```bash
	uv add --dev git+https://codeberg.org/so-rose/blext.git
	```
	!!! tip
		See [`uv` git source](https://docs.astral.sh/uv/concepts/projects/dependencies/#git) for more on how to choose specific tags, branches, commits, etc. .

**Finally**, run `blext` using the prefix `uv run`, like this:
```bash
uv run blext --help  ## $(pwd) must be within a `uv` project.
```


!!! tip
	Confused about why to install `blext` per project, when you also have it globally installed?

	- **Future Proofing**: By locking the _specific version_ of `blext` used to build your extension, you guarantee that new versions of `blext` won't spontaneously break your extension.
	- **Easy Collaboration**: By forcing all contributors to use the same version of `blext`, there won't be any issues






### Install w/`venv`
**Global** method using a manually created virtual environment.

=== "Linux"
	!!! warning
		Your system's Python version must be compatible with `blext`.
		If it isn't, you might get this error message:

		```
		$ pip install blext
		ERROR: Could not find a version that satisfies the requirement blext (from versions: none)
		ERROR: No matching distribution found for blext
		```

	**First**, navigate to an empty folder in a central location:
	```bash
	MY_BLEXT_FOLDER="$HOME/blext"  ## Configure as you wish
	mkdir "$MY_BLEXT_FOLDER"
	cd "$MY_BLEXT_FOLDER"
	```

	**Then**, create a virtual environment and install `blext` into it:
	```bash
	python3 -m venv .venv  ## or just 'python'; depends on how Python is installed.
	source .venv/bin/activate
		pip install --upgrade pip
		pip install --upgrade blext
	deactivate
	```

	`blext` can now be run from anywhere using:
	```bash
	"$MY_BLEXT_FOLDER/.venv/bin/blext" --help
	```

	This may seem a little verbose.
	If `$HOME/.local/bin` is on your `PATH`, run
	```bash
	ln -s "$MY_BLEXT_FOLDER/.venv/bin/blext" $HOME/.local/bin
	```
	to make the `blext` command available globally.

	Make sure to test that the command is found:
	```
	$ whereis blext
	blext: /home/user/.local/bin/blext
	```

	!!! tip
		On many Linux distributions, the standard place to put locally installed executable software is `$HOME/.local/bin`.

		For this to work:

		- `$HOME/.local/bin` must exist.
		- The system's `PATH` variable must contain `$HOME/.local/bin`.

		Here's how to get it to work:

		1. If the folder doesn't exist, create it:
		```bash
		mkdir $HOME/.local/bin
		```

		2. Check if your `PATH` variable contains `$HOME/.local/bin`:
		```bash
		echo "$PATH"
		```

		3. If not, add the following snippet to your `$HOME/.profile`:
		```bash
		if [ -d "$HOME/.local/bin" ] ; then
			PATH="$HOME/.local/bin:$PATH"
		fi
		```

		**You must log out and in after altering `.profile`, for it to take effect.**
		After re-logging, you can try re-linking `blext`:
		```bash
		ln -s $(pwd)/.venv/bin/blext $HOME/.local/bin
		```

=== "MacOS"
	TBD. For now, the Linux instructions might work.

=== "Windows"
	TBD.

---

### Install w/`pip` (**discouraged**)
!!! danger
	We **strongly discourage** using `pip`/`pip --user` to install packages globally:

	- **Uninstall Doesn't Clean Up**: When you install, then uninstall, a package with `pip`, its dependencies _are not_ cleaned up. They will persist _forever_ in your **global site-packages**, wreaking havoc with little recourse.
	- **Global Dependency Conflicts**: `pip` cannot handle situations where two different packages need incompatible versions of the same dependency. Sooner or later, _this will happen_, and something _will break_, with little recourse.

	For more, see the following:

	- Uninstalling `pip` Packages: <https://stackoverflow.com/questions/7915998/does-uninstalling-a-package-with-pip-also-remove-the-dependent-packages>
	- Dependency Conflicts: <https://stackoverflow.com/questions/75407687/dealing-with-pip-install-dependency-conflicts>

	If you're unsure of what to do, **strongly consider** using a `uv`-based installation method.
```bash
pip install --user blext
```

!!! tip
	`blext` uses `uv` as a dependency.

	Therefore, even though you didn't install `uv`, it can still be run using
	```bash
	blext uv
	```

	This can be convenient for tasks like adding dependencies to single-file script extensions:
	```bash
	blext uv add --script my-script.py scipy
	```



## Alternative Installation Methods
### Run w/`uvx`
Launches `blext` without explicit installation, using the `uvx` command from the [`uv` project manager](https://docs.astral.sh/uv/).

!!! warning
	This installation method requires [`uv`](https://docs.astral.sh/uv/) to be correctly installed beforehand, since every `blext` project is also a `uv` project.
 
	Please refer to the [`uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/).

Whenever you wish to run `blext`, you should write `uvx blext@latest` instead, like this:
```
$ uvx blext@latest --help  # equiv. to 'blext --help'
Usage: blext COMMAND
...
```

For more on how this works, see the [`uv` tools documentation](https://docs.astral.sh/uv/concepts/tools/).

!!! tip
	You don't have to add `@latest`.
	You can, instead, just run
	```
	$ uvx blext --help
	Usage: blext COMMAND
	...
	```
	and it will use the cached version of `blext`, even if it's older than the latest version.

	**Note that `blext` won't automatically update when running this command.**



## Tips and Tricks
!!! info
	Any **global** installation of `blext` ensures that you can run `blext` commands from anywhere, like this:

	```bash
	blext --help
	```

!!! info
	A **per-project** installation of `blext` ensures that you can run `blext` commands from within that project, like this:

	```bash
	uv run blext --help
	```

	**With a per-project install, the ability to build an extension is protected from changes to `blext`.**

!!! question "How do I install a specific `git` tag/branch/commit?"
	Any `uv`-based method (including [`uv tool`][install-wuv-tool-recommended] and [`uv add --dev`][install-wuv-add-dev-recommended]) works with any so-called `uv` source.

	The `git` source allows specifying options like `--branch` or `--tag`, which have the desired effect.
	For example:
	```bash
	uv add git+https://codeberg.org/so-rose/blext.git --branch main
	```

	See [`uv` git source](https://docs.astral.sh/uv/concepts/projects/dependencies/#git) for more.

!!! question "What is `uvx`? Is it magic?"
	It is magic!

	[`uvx`](https://docs.astral.sh/uv/#tools) is a command that comes with the [`uv` project manager](https://docs.astral.sh/uv/), which allows Python programs to be downloaded and run in one command, with its dependencies fully isolated.

	For example, to use the `ruff` linter without installing it, just write:
	```
	uvx ruff@latest --version
	```

!!! question "Do I have to install [`uv`](https://docs.astral.sh/uv/) in order to use `blext`?"
	**Not strictly**, but not installing `uv` is probably a bad idea.

	`blext` assumes that several things about managing Python projects are easy.
	Without `uv`, they are not always so easy:

	- **Dependency Management**: `uv add` and `uv add --script` is a very convenient way to manage dependencies of `pyproject.toml` files / of inline script metadata.
	- **Project Management**: `uv sync` builds a `.venv` that is _almost_ identical to the one inside of Blender. `uv tree` gives you an overview of your extension's platform-independent dependency graph. _These features are out-of-scope for `blext`, since `uv` already does the job really well_.

	If this is something you need, we'd love to hear more - feel free to contact us, and at the very least, we can help clarify things.
