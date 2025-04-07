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
> `blext` should be considered **alpha software** aka. **unstable**.
> 
> - The UX may have unsolved frustrations or hiccups.
> - Features may be incomplete, buggy, or misleadingly documented.
> - The documentation may be incomplete or outdated.
> - The test suite has no guarantees of coverage or passing.
> 
> With that said, we already personally find `blext` **quite useful**, and hope you will too.



## Highlights
- 🛠 **Welcome to Modern Python**: `blext` extensions are _standard_ Python, managed by the cutting-edge [`uv` project manager](https://docs.astral.sh/uv/). _Welcome to the modern Python ecosystem!_
- 🚀 **Snappy at Scale**: Create, download, build, analyze, and run _gigabyte_-sized extensions in moments, without hacks. _What you run is what the user runs._
- 📦 **Fearless PyDeps**: "Just `uv add scipy`"! Never be scared of adding Python dependencies to your extension again - `blext` handles compatibility with the VFX reference platform, dependency resolution, and cross-platform wheel selection. _We also got tired of choosing wheel tags._
- 🏢 **Robust by Design**: We believe that great tools comes from well-chosen, well-integrated abstractions, presented concisely.
We keep ourselves honest with static typing, strict linting, and `pydantic`-powered data modelling.
_`blext` strives to become your swiss-army knife of extension-making._
- 🌐 **Respects your Freedoms**: `blext` preserves your freedom to use, modify, fork, redistribute, or even sell `blext`, **so long as you extend the same freedoms as you were granted** under the [AGPL](https://www.gnu.org/licenses/agpl-3.0.html) software license. _For more details, see our [License Policy](https://docs.sofus.io/blext/stable/reference/policies/licensing.html)._

**Want to know more?** See [Features](https://docs.sofus.io/blext/stable/features.html).



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
