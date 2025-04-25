!!! abstract
	Get going with `blext` by making a small extension!

# Getting Started
!!! warning
	It is **strongly suggested** to install [`uv`](https://docs.astral.sh/uv/) before following this guide, using the [`uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/).

	`uv` makes installing `blext` easy to do properly; therefore, this guide presumes that `uv` is available.
	For methods that don't require `uv`, see [Installation](../installation.md).

1. **Install `blender`**: Check out the [official Blender downloads](https://www.blender.org/download/).

1. **Install `blext`** - of course!

<!-- termynal -->
```
$ uv tool install blext@latest
Resolved 27 packages in 110ms
Audited 27 packages in 0.22ms
Installed 1 executable: blext
```

_That's it! Let's make an extension._



## Suzanne's First Extension
`cd` to your favorite folder (we suggest ex. `$HOME/src`), and run:
```
$ blext init hello-suzanne
...
```

That's it!
Enter the folder
```
cd hello-suzanne
```
and try the extension in Blender's GUI:
```
blext run
```

So far so good!

!!! tip
	This `blext` project extension locks a specific version of `blext`!

	This means that everyone interacting with your project uses _your project's_ version of `blext` to build, run, analyze, etc. .
	That leaves you free to adopt new `blext` features without all contributors needing to update their `blext` version.

	For convenience, `blext` commands will always **auto-proxy themselves to the project-local `blext` version**:
	```
	$ blext run
	Using project-local blext

	...
	```

	_In `uv` terminology, this is effectively the same as:_
	```
	$ uv run blext run
	...
	```



## Configuring the Extension
To configure Blender extensions, `blext` looks for appropriate fields in `pyproject.toml`, then generates a `blender_manifest.toml`.

To see the generated `blender_manifest.toml` file, run:
```toml
$ blext show blender_manifest
schema_version = "1.0.0"
...
```

Now, let's try to add some `tags`, which helps users categorize our extension's functionality.

Open `pyproject.toml` using your text editor of choice.
Find `[tool.blext]`, and add a `bl_tags` field underneath it:

```toml
[tool.blext]
bl_tags = ["User Interface"]
```

Like magic, the generated `blender_manifest.toml` now includes the tag!
```toml
$ blext show blender_manifest
schema_version = "1.0.0"
...
tags = [
    "User Interface",
]
...
```

You can also validate the tag's presence in Blender's GUI:
```
blext run
```


!!! question "How do I know which fields to use?"
	For a complete guide to available fields, see [Config / Extension Config](./config/extension_config.md).

!!! tip
	The errors shown by `blext` are carefully crafted to be both **strict and helpful**.

	Our best advice is therefore to **always read the errors carefully**.
	To the extent possible, `blext` errors come with not only an explanation, but a list of possible problems and common remedies.

	This way, whether you forgot to add a required field, or trying to figure out something hairier like raising the `min_macos_version`, you shouldn't have to feel completely lost.




## Adding Python Dependencies
Say you forgot the speed of light.
Hey, it happens!
Luckily, [`scipy` has your back](https://docs.scipy.org/doc/scipy/reference/constants.html#module-scipy.constants).
```python
import scipy.constants
print(scipy.constants.speed_of_light)
```

To make such `import scipy` statements work inside of your extension, just run:
```
blext add dep scipy
```

**That's it**!
You can now `import scipy` anywhere in your extension code, on any platform supported by your extension.

!!! warning
	`scipy` depends on `numpy`.
	However, `numpy` is already shipped with Blender.
	**Not only** must `numpy` never be included, but `scipy` **must** be guaranteed compatible with the `numpy` that's already in Blender!

	`blext` (feat. `uv`) handles this **automatically**.
	`blext add dep` always selects a version of `scipy` that works with Blender's `numpy`, or throws an error explaining that no available version of `scipy` works.

!!! tip
	At this point, **we highly suggest** familiarizing yourself with the basics of the [`uv` package manager](https://docs.astral.sh/uv/).

	- All `blext` projects are also `uv` projects, and are fundamentally managed using `uv`.
	- In some cases, `blext` acts as a thin wrapper over `uv` commands.

	`blext` and `uv` were designed to be used together, especially when it comes to Python dependencies.



## Distribution
To build packed extension `.zip`s for all supported platforms, just run:
```
$ blext build
...
```

A series of checks will be run automatically on the packed `.zip`s, to help catch some of the most obvious issues.
These can also easily be run manually, without generating `.zip` files:
```
$ blext check
...
```

After your extension reaches a certain maturity, you may wish to submit your extension for review on the [official Blender extensions platform](https://extensions.blender.org)!

!!! warning
	Please respect the limited resources of the official extension platform by making sure your extension is of high quality and fit for wider use.
	
	To help you make sense of what they expect, we've gathered a bespoke collection of resources as [Resources / Extension Resources](../resources/extension_resources.md).



## Next Steps
In this guide, you've created an extension, configured it, added Python dependencies, and built it for wider distribution.
You're well on your way to being a `blext` pro!

Still, this guide only scratches the surface of what `blext` can do.

!!! tip
	Did you know that you can make single-file "script extensions"? See [Script Extensions](script_extensions.md).

	Did you know `blext` can build and run extensions directly from a URL? See [CLI / Options](cli/options.md) for more on how extensions can be located.

	Been holding off on migrating your addon to an extension? See [Migrating / from Legacy Addon](migrating/from_legacy_addon.md) for more on how `blext` can make that process easier.

	Ready to dig deeper into extension configuration? See [Config / Extension Config](config/extension_config.md) for a description of all fields.
