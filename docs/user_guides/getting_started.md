# Getting Started
1-2-3, and you're ready to go!

1. **Install `blender`**: Check out the [official Blender downloads](https://www.blender.org/download/).
2. **Install `uv`**: Check out the [official `uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/).
3. **Install `blext`**: Just run `uv tool install blext`.
	- For all installation methods, see [Installation](../installation.md).

## First Extension

`cd` to your favorite folder and run:
<!-- termynal -->
```
$ blext init first-extension
Something something it worked
```

Now, enter the new extension folder
```
cd first-extension
```
and run it in Blender: [^1]
```
blext run
```

[^1]:
	Anyone who builds your extension will automatically do so with the exact same version of `blext`, with no action on your part.

	But how? `blext` is actually a dependency of your extension project!
	Usually, you'd have to write `uv run blext` to run a project dependency - but we thought that was repetitive.

	So, when there's a project version of `blext`, we made `blext` automatically proxy anything you give it to `uv run blext` instead.



## Configuring the Extension
TODO



## Adding PyPi Dependencies
!!! tip
	At this point, **we strongly suggest** familiarizing yourself with the basics of the [`uv` package manager](https://docs.astral.sh/uv/).

	- All `blext` projects are also `uv` projects, which can be managed using `uv`.
	- `blext` doesn't "wrap" functionality of `uv` that already works well.

	`blext` and `uv` were designed to be used together, especially when it comes to Python dependencies.

Say you forgot the speed of light.
Luckily, [`scipy` has your back](https://docs.scipy.org/doc/scipy/reference/constants.html#module-scipy.constants)!
All you need to do is:

```python
import scipy
print(scipy.constants.speed_of_light)
```

To make `import scipy` work inside of your extension, just run:
```
uv add scipy
```

**That's it**!
You can now `import scipy` anywhere in your extension code, across platforms.

### Analyzing Dependencies
To see which "wheels" in particular are pulled in, run: [^1]
<!-- termynal -->
```
$ blext show deps
┏━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Name      ┃ Version ┃ Platforms        ┃ Py|ABI      ┃ Size      ┃
┡━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ numpy     │ 1.24.4  │ macosx_11_0_arm… │ cp311|cp311 │ 13.8 MB   │
│ numpy     │ 1.24.4  │ manylinux_2_17_… │ cp311|cp311 │ 17.3 MB   │
│ numpy     │ 1.24.4  │ win_amd64        │ cp311|cp311 │ 14.8 MB   │
│ scipy     │ 1.15.2  │ macosx_12_0_arm… │ cp311|cp311 │ 30.1 MB   │
│ scipy     │ 1.15.2  │ manylinux_2_17_… │ cp311|cp311 │ 37.6 MB   │
│ scipy     │ 1.15.2  │ win_amd64        │ cp311|cp311 │ 41.2 MB   │
├───────────┼─────────┼──────────────────┼─────────────┼───────────┤
│ =6 wheels │         │ macos-arm64,     │             │ =154.9 MB │
│           │         │ windows-x64,     │             │           │
│           │         │ linux-x64        │             │           │
└───────────┴─────────┴──────────────────┴─────────────┴───────────┘
```

[^1]:
	When a dependency eg. `numpy` is defined in the [VFX Reference Platform](https://vfxplatform.com/), `blext` won't download or include it in extensions, or show it in the dependency overview.

	Instead, `blext` will enforce that incompatible version of eg. `numpy` are never asked for, even if that makes it impossible to install a requested dependency.
