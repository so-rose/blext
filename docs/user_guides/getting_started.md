# First Steps
1-2-3, and you're ready to go!

1. **Install `blender`**: Check out the [official Blender downloads](https://www.blender.org/download/).
2. **Install `uv`**: Check out the [official `uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/).
3. **Install `blext`**: We suggest a [global installation w/`uv tool`][install-wuv-tool-recommended].
See the [install guide](installation.md) for more.

`cd` to your favorite folder and run:
<!-- termynal -->
```
$ blext init first-extension
Something something it worked
```

Enter the extension folder and test it out!



!!! tip
	At this point, **we suggest** familiarizing yourself with the basics of the [`uv` package manager](https://docs.astral.sh/uv/).

	- All `blext` projects are also `uv` projects, which can be managed using `uv`.
	- `blext` doesn't "wrap" functionality of `uv` that already works well.

	`blext` and `uv` were designed to be used together, so we promise this will pay off.
