# Options
Several of `blext`'s CLI commands share the same syntax for accomplishing the same things.

By combining the flexibility of this syntax with the capabilities of underlying commands, one can accomplish a lot more with `blext`!


## Locating Extensions
Commands like `blext build` are always in reference to ex. the extension that one wishes to build.
But how does one find that extension?

**Locations**: `blext` looks for extensions at "locations".

- [Filesystem Path][by-path]: The project/script/packed extension is in a local filesystem.
- [HTTP URL][by-url]: The project/packed extension is on the internet.
- [`git` Remote][by-git-repository]: The project/script/packed extension is in some `git` repository.

**Sources**: `blext` can detect the following extension "sources".

- [Project Extensions](../project_extensions.md): Extensions built from a Python project, configured using `pyproject.toml`.
- [Script Extensions](../script_extensions.md): Extensions built from a single `*.py` file.
- **Packed Extensions**: `blext` can parse already-packed Blender extensions _backwards_ into a `blext` extension! _This makes it super easy to ex. repack an extension for different platforms._

!!! example "How To: Run Remote Script Extension"
	```
	$ blext run https://example.com/my-blext-extension.py
	```

!!! example "How To: Build Latest Remote `git` Project for `linux-x64`"
	```
	$ blext build git+https://example.com/my-blext-extension.git --platform linux-x64
	```

!!! info
	In this section, the funny little symbol `$0` is used a lot.

	`$0` refers to the **first positional argument** of any command that locates extensions.

	**For example**:

	- For `blext build hello-blender`, `$0` is `hello-blender`.
	- For `blext check test-extension.zip`, `$0` is `test-extension.zip`.




### by Default
!!! example "How To: Build Current `blext` Project"
	Within the project directory, run:
	```
	$ blext build  ## Implicitly finds 'pyproject.toml' in the current dir.
	```

	This will search for a `pyproject.toml` file in the current directory, as well as any parent directories.



### by Path
`$0 | script+$0 | project+$0 | packed+$0 | --path.script | --path.project | --path.packed`

!!! example "How To: Build Specific `blext` Project"
	```
	$ blext build my-blext-extension
	```

	Alternatively, `--path` can be passed explicitly:
	```
	$ blext build --path my-blext-extension/pyproject.toml
	```


!!! example "How To: Validate a Script Extension"
	```
	$ blext check my-blext-extension.py
	```

**Detection**: The following paths can be used as `$0`.

- **Current Folder** (_default_): Search upwards for a `pyproject.toml`.
- **Project File** (`path -> pyproject.toml`): Path to an extension config file.
- **Project Folder** (`path / 'pyproject.toml'`): A folder that contains `pyproject.toml`.
- **Script File** (`*.py`): A script extension.
- **Packed Extension** (`*.zip`): A packed Blender extension extension.




### by URL
`http://$0 | script+http://$0 | packed+http://$0 | --url.script | --url.packed`

!!! example "How To: Validate Remote Script Extension"
	```
	$ blext check https://example.com/my-blext-extension.py
	```
	or:
	```
	$ blext check --url.script https://example.com/my-blext-extension.py
	```

!!! example "How To: Validate Remote Packed Extension"
	```
	$ blext check packed+https://example.com/my-blext-extension.zip
	```
	or:
	```
	$ blext check --url.project https://example.com/my-blext-extension.zip
	```

- `$0`: Detect an extension at `url = $0`, using its `Content-Type` header.
- `script+$0`: Locate a script extension at `url = $0`.
- `packed+$0`: Locate a packed extension at `url = $0`.

**Detection**: The following `Content-Type`s are interpreted on `$0`.

- **Script File** (`text/plain`): URL of a script extension.
- **Packed Extension** (`application/zip`): URL of a packed Blender extension.



### by `git` Repository
`git+$0 | --git.url` including optional constraints:

- `--git.rev`: Reference to a particular commit.
- `--git.tag`: Reference to a particular tag.
- `--git.branch`: Reference to the head of a particular branch.
- `--git.entrypoint`: Path to an extension within the repository (path is relative to the repo root).

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


When `--git.entrypoint` is given, the path-detection logic in [Locating by Path][by-path] will be used to deduce whether a project, script, or packed extension is referenced.

Otherwise, a project extension will always be attempted built, by searching for `pyproject.toml` in the repository root.



## Constraining `blext` Extensions
**How is the `blext` project constrained?**

- [Platform][to-platforms]: Select a subset of extension platforms to support.
- [Release Profiles][to-release-profiles]: Alter the extension's settings for a particular use case.

_All commands locate `blext` project can also constrain them using options defined in this section._

### to Blender Versions
`--bl-version`: One of the supported Blender versions between `tool.blext.blender_version_min` and `tool.blext.blender_version_max`.

!!! example "How To: Build for Blender 4.3.6"
	```
	$ blext build my-blext-extension --bl-version bl4-3-0
	```

### to Platforms
`--platform`: One of the platforms defined in `tool.blext.supported_platforms`.

!!! example "How To: Build a Linux (x64) Version of a Script Extension"
	```
	$ blext build my-blext-extension.py --platform linux-x64
	```

!!! example "How To: Show Project Extension Dependencies for Locally-Detected Platform"
	```
	$ blext show deps my-blext-extension.py --platform detect
	```

- **Choices**: `linux-x64`, `linux-arm64`, `macos-x64`, `macos-arm64`, `detect`.
- **Default**: All `tool.blext.supported_platforms`.

_Can be specified several times, to specify several platforms._



### to Release Profiles
`--profile`: One of the "release profiles" defined by default / in `tool.blext.profiles`.

!!! example "How To: Prepare a Release-Debug Build of a Project Extension, from a URL"
	```
	$ blext build project+https://example.com/my-blext-extension.zip --profile release-debug
	```

- **Choices**: `test`, `dev`, `release`, `release-debug`, `$custom`.
- **Default**: All `tool.blext.supported_platforms`.

_Any `$custom` profile defined in `pyproject.toml` can also be specified._
