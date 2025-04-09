# `blext`: Modern Blender Extension Development
`blext` makes it easy to develop Python extensions for [Blender](https://www.blender.org/).

---

**Documentation**: <https://docs.sofus.io/blext>

- _NOTE: The documentation is not live yet. Stay tuned!_

**Source Code**: <https://codeberg.org/so-rose/>

**PyPi Package**: <https://pypi.org/project/blext/>

---

> [!NOTE]
> **Please submit Issues to the [Codeberg repository](https://codeberg.org/so-rose/)** (_you can login with GitHub_)

> [!WARNING]
> `blext` is under heavy development, and should be considered **alpha software** aka. **unstable**.
> 
> - **Features may be missing, incomplete, buggy, or misleadingly documented**.
> - `main` may break without warning, and the `PyPi` version may be extremely out of date.
> - The UI/UX may have unsolved frustrations,  or be misleading.
> - The documentation may be incomplete, outdated, or simply non-existant.
> - Tests, if they exist, have no guarantees of coverage or passing.
> 
> We already personally find the `main` branch of `blext` **quite useful**, and we invite you to give it a try!
> _Above all else, please be patient with us at this early stage._



## Highlights
- 🛠 **Welcome to Modern Python**: `blext` extensions are standard Python projects, powered by the cutting-edge [`uv` project manager](https://docs.astral.sh/uv/) and a standard `pyproject.toml`.
- 🚀 **Snappy at Scale**: Create, download, build, analyze, and run large extensions in moments, without resorting to fragile mechanisms that fracture deployment from development.
- 📦 **Fearless PyDeps**: "Just `uv add scipy`"! Never be scared of adding Python dependencies to your extension again - `blext` handles VFX reference platform compatibility, dependency resolution, and cross-platform wheel selection. _We also got tired of choosing wheel tags._
- 🗂️ **Swiss-Army Knife of Extensions**: `blext` is more than a build system - it's a complete suite of tools for dealing with extensions.
- 🛠 **Code Transforms**: `blext` can automatically perform certain "safe" code rewrites, such as AST-level rewrite of absolute imports to relative imports.
- 🏢 **Robust by Design**: We believe that great tools comes from well-chosen, well-integrated abstractions, presented concisely.
- 🌐 **Respects your Freedoms**: `blext` preserves your freedom to use, modify, fork, redistribute, or even sell `blext`, **so long as you extend the same freedoms as you were granted** under the [AGPL](https://www.gnu.org/licenses/agpl-3.0.html) software license. _For more details, see our [License Policy](https://docs.sofus.io/blext/stable/reference/policies/licensing.html)._

**Want to know more?** See [Features](https://docs.sofus.io/blext/stable/features.html).


> [!WARNING]
> While many features already work, some features may be **missing / work-in-progress**.
> 
> See [Features](https://docs.sofus.io/blext/stable/features.html) for a detailed overview of what does and doesn't work right now.




## Quickstart
**Ready to make extensions**? Skip directly to [Getting Started](https://docs.sofus.io/blext/stable/user_guides/getting_started.html).

**Just want to give it a try**? If [`uv`](https://docs.astral.sh/uv/) is [correctly installed](https://docs.astral.sh/uv/getting-started/installation/), you can start using `blext` right away:

<!-- termynal -->
```
$ uvx blext@latest --help
Usage: blext COMMAND
...
```

> [!TIP]
> You can follow the [Getting Started Guide](https://docs.sofus.io/blext/stable/user_guides/getting_started.html) without installing `blext`, using `uvx` like this.
> 
> Just make sure to write `uvx blext@latest` instead of `blext`, whenever you run a `blext` command.

**Want to install `blext` permanantly**? See our [Installation Guide](https://docs.sofus.io/blext/stable/installation.html).

> [!NOTE]
> **NOTICE: Hot Takes Wanted**

> **Share your experience** with us in our [Issues system](https://codeberg.org/so-rose/blext/issues) (supports GitHub login)!
> 
> We would appreciate if you took a moment to _assign a label_ to your the Issues:
> 
> - `user-report`: You tried it, and have some constructive opinions to share!
> - `ux`: Something was frustrating that didn't need to be.
> - `bug`: Something's not working the way it's supposed to.
> 
> See all labels here: <https://codeberg.org/so-rose/blext/labels>


## Acknowledgements
`blext` is a love letter to the [Blender](https://www.blender.org/) community, provided in hopes that it might be useful.

We would like to thank [Astral](https://astral.sh/) for creating `uv`, an exceptionally crafted tool that both inspires and powers `blext`.
The Rust project manager, [`cargo`](https://github.com/rust-lang/cargo) also deserves a lot of credit for inspiring `blext`.

Finally, we encourage you to peruse our `uv tree` of dependencies.
We stand on the shoulders of giants, and could not hope to see so far without.
