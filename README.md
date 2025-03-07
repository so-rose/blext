# `blext`: Modern Blender Extension Development

---

**Documentation**: <https://docs.sofus.io/blext>

**Source Code**: <https://codeberg.org/so-rose/>

**PyPi Package**: <https://pypi.org/project/blext/>

---
`blext` makes it easy to develop Python extensions for [Blender 3D](https://www.blender.org/).

!!! danger "Danger: Alpha Software"
	`blext` should be considered alpha software aka. **unstable**.

	- The UX may have unsolved frustrations or hiccups.
	- Features may be incomplete, buggy, or misleadingly documented.
	- The documentation may be incomplete or outdated.
	- The test suite has no guarantees of coverage or passing.

	With that said, we already personally find `blext` **quite useful**, and hope you will too.



## Highlights
- 🛠 **Extensions are Python Projects**: `blext` manages "Blender extensions" as standard Python projects, defined using either `pyproject.toml` or single-file scripts with [`PEP 723` inline script metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata).
- 💭  **Helpful and Opinionated**: By being opinionated about how Blender extensions should be made, `blext` can often offer not only a description, but a solution, when errors are encountered that would prevent a standards-compliant extension from being built.
- 🚀 **Snappy at Scale**: Build, run, and edit your Blender extension with minimal overhead, even for extensions that use _gigabytes_ of wheels.
- 📦 **Fearless PyDeps**: Fearlessly add Python dependencies, confident that `blext` will work out all the gritty cross-platform details. _No more vendorizing, tracking down platform tags, and other such nonsense: If your extension needs `scipy`, just `uv add scipy`_.
- 🏢 **Robust by Design**: `blext` aims to be your _swiss-army knife_ of extension development.
Our analysis suite consists of `ruff` and strict-mode `basedpyright`, and our design process emphasizes immutable, narrowly types parsing.
Finally, **`blext` follows [semantic versioning](https://semver.org/)**, helping you judge which updates are safe for your extension project.
- 🌐 **Respects your Freedoms**: `blext` preserves your freedom to use, modify, fork, redistribute, or even sell `blext`, **so long as you extend the same freedoms as you were granted**. For more, see the [AGPL](https://www.gnu.org/licenses/agpl-3.0.html) software license.

**For more details** see [Features ](features.md).

_If you'd like to use `blext`, but your organization prohibits the use of AGPL software, please contact the authors - we would be happy to arrange a different licensing scheme, for a fee._



## Quickstart
**Ready to make extensions**? Check out the [First Steps Guide](user_guide/first_steps.md).

**Just want to give it a try**? If [`uv`](https://docs.astral.sh/uv/) is [correctly installed](https://docs.astral.sh/uv/getting-started/installation/), you can start using `blext` command without any special installation steps:

<!-- termynal -->
```
$ uvx blext@latest --help
Usage: blext COMMAND
...
```



### Installation
See the [Installation](installation.md) docs.

!!! tip
	You can follow the [First Steps Guide](user_guide/first_steps.md) without installing `blext`, using `uvx` like this.

	Just make sure to write `uvx blext@latest` instead of `blext` whenever you're outside of an extension project.



## Contributing
!!! feedback "Hot Takes Wanted"
	**Please share your experiences** with us in our [Issues system](https://codeberg.org/so-rose/blext/issues), which supports GitHub login.

	We would appreciate if you took a moment to _assign a tag_ to your the Issues:

	- `user-experience`: You tried it, and have some constructive opinions to share!
	- `ux`: Something was frustrating that didn't need to be.
	- `bug`: Something's not working the way it's supposed to.

	See all labels here: <https://codeberg.org/so-rose/blext/labels>



## Acknowledgements
`blext` is a love letter to the [Blender](https://www.blender.org/) community.
Having spent months solving problems that we ourselves encounter and see, we dearly hope this little tool can be of use.

We would like to thank [Astral](https://astral.sh/) for creating `uv`, an exceptionally crafted tool that makes `blext` possible.
The Rust project manager, [`cargo`](https://github.com/rust-lang/cargo) also deserves a lot of credit for inspiring `blext`.

Finally, we encourage you to peruse `uv tree` of dependencies.
We stand on the shoulders of giants
