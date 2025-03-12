# Options: Locating
**Where does the `blext` project come from?**

- [Path][by-path]: A project or script extension on your local filesystem.
- [Script URL][by-script-url]: A script extension somewhere on the internet.
- [Project URL][by-project-url]: A project extension somewhere on the internet, packed in a source-code `.zip` file.
- [`git` Repository][by-git-repository]: A project or script extension in a local or remote `git` repository.

_All commands that need to locate a `blext` project take options defined in this section._

!!! example "How To: Run Remote Script Extension"
	```
	$ blext run script+https://example.com/my-blext-extension.git
	```

!!! example "How To: Validate Remote Script Extension"
	```
	$ blext check script+https://example.com/my-blext-extension.git
	```




## by Path
`$0 | --path | -p`: Path to a `blext` project.
The following kinds of paths are valid:

- **Current Directory** (_default_): Search upwards for a `pyproject.toml`.
- **Project File** (`pyproject.toml`): `blext` project config, specified directly.
- **Project Folder** (`(*)/pyproject.toml`): Folder containing a `pyproject.toml`.
- **Script File** (`*.py`): A script extension, specified directly.

!!! example "How To: Build Current `blext` Project"
	Within the project directory, run:
	```
	$ blext build  ## Implicitly finds 'pyproject.toml' in 
	```

	This will search for a `pyproject.toml` file in the current directory, as well as any parent directories.

!!! example "How To: Build Specific `blext` Project"
	```
	$ blext build --path my-blext-extension/pyproject.toml
	```

	For convenience, `--path` can be omitted, as can `pyproject.toml`:
	```
	$ blext build my-blext-extension
	```

!!! example "How To: Validate a Script Extension"
	```
	$ blext check --path my-blext-extension.py
	```

	For convenience, `--path` can be omitted
	```
	$ blext check my-blext-extension.py
	```



## by Script URL
`script+$0 | --url.script`: URL to a script extension.

- **Script File** (`*.py`): The URL must resolve to a `.py` defining a script extension.

!!! example "How To: Validate Remote Script Extension"
	```
	$ blext check script+https://example.com/my-blext-extension.py
	```
	or:
	```
	$ blext check --url.script https://example.com/my-blext-extension.py
	```



## by Project URL
`project+$0 | --url.project`: URL to a `.zip` of a project extension.

- **Project Zip** (`*.zip`): The URL must resolve to a `.zip` file, containing a `pyproject.toml`.

!!! example "How To: Validate Remote Project Extension"
	```
	$ blext check project+https://example.com/my-blext-extension.zip
	```
	or:
	```
	$ blext check --url.project https://example.com/my-blext-extension.zip
	```



## by `git` Repository
`git+$0 | --git.url`: URL of a `git` repository, optionally constrained further by:

- `--git.rev`: Reference to a particular commit.
- `--git.tag`: Reference to a particular tag.
- `--git.branch`: Reference to the head of a particular branch.
- `--git.entrypoint`: Path to an extension specification file, relative to the repo root.

!!! example "How To: Run Project Extension in `v5.3.3` Tag of `git` Repository"
	```
	$ blext run git+https://example.com/my-blext-extension.git \
		--git.tag v5.3.3
	```
	or:
	```
	$ blext run --git.url https://example.com/my-blext-extension.git \
		--git.tag v5.3.3
	```

!!! example "How To: Build Script Extension in `HEAD~1` Commit of `cool-new-feature` Branch"
	Consider a repo w/a script extension at `examples/new-feature-test-extension.py`.

	This can be run locally, in Blender, using:
	```
	$ blext run git+https://example.com/my-blext-extension.git \
		--git.branch cool-new-feature \
		--git.rev HEAD~1 \
		--git.entrypoint examples/new-feature-text-extension.py
	```
