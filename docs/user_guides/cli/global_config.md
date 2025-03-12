# Options: Global Config
`blext`'s operation may be altered using a number of "global" configuration fields:


!!! danger
	**Not to be confused** with extension configuration in `pyproject.toml`.

	- **Global Configuration** _changes how `blext` itself works_, in a global `config.toml`.
	- **Extension Configuration** _changes how a `blext` project_ works, in a project `pyproject.toml`.

## File Location
The global configuration file is placed in an appropriate location, depending on the platform:

- **Linux**: `$HOME/.config/blext/config.toml`
- **MacOS**: `$HOME/Library/Application Support/blext/config.toml`
- **Windows**: `$HOME\\AppData\\Local\\blext\\blext\\config.toml`

!!! tip
	If you're unsure of where your global config is located, you can always run:
	```
	$ blext show path global_config
	```

!!! note
	These paths are derived from the [`platformdirs`](https://platformdirs.readthedocs.io/en/latest/index.html) library, like this:
	```python
	import platformdirs
	platformdirs.user_config_dir('blext', 'blext')
	```

	If you're using a completely different platform, please refer to the `platformdirs` documentation to locate your global configuration file.

!!! warning
	There is currently no way to alter the global configuration file location.

	If this is something you need, please submit an Issue to start the conversation.

## Global Config Fields
|          Config         	|  Type  	|               Description               	|
|:-----------------------:	|:------:	|:---------------------------------------:	|
| `cfg.path_global_cache` 	| `Path` 	| Global cache directory of  `blext`.     	|
| `cfg.path_blender_exe`  	| `Path` 	| Path to  `blender` executable. 	|
| `cfg.path_uv_exe`       	| `Path` 	| Path to `uv` executable.       	|

!!! tip
	You can always show your current global configuration using:
	```
	$ blext show global_config
	```

	Since this effectively _generates_ a global config file, you can easily script generating a new global config file:
	```bash
	blext show global_config > $(blext show path global_config)
	```

!!! example
	For a user `user` on Linux, using the `uv tool` installation method, the default `config.toml` might look like:
	```toml
	[cfg]
	path_global_cache = "/home/user/.cache/blext"
	path_blender_exe = "/home/user/.local/bin/blender"
	path_uv_exe = "/home/user/.local/share/uv/tools/blext/bin/uv"
	```

## Configure via CLI / Environment
It is possible to _temporarily_ override global config entries using env vars and/or CLI options.

|          Config         	|            Env            	|            CLI            	|
|:-----------------------:	|:-------------------------:	|:-------------------------:	|
| `cfg.path_global_cache` 	| `BLEXT_PATH_GLOBAL_CACHE` 	| `--cfg.path_global_cache` 	|
| `cfg.path_blender_exe`  	| `BLEXT_PATH_BLENDER_EXE`  	| `--cfg.path_blender_exe`  	|
| `cfg.path_uv_exe`       	| `BLEXT_PATH_UV_EXE`       	| `--cfg.path_uv_exe`       	|

!!! example "Build Script Extension w/Temporary Global Cache Path"
	Since script extensions always use the global path, you might want to alter that path temporarily:
	```
	$ blext build script-extension.py --cfg.path_global_cache /home/user/special-blext-cache
	```

!!! example "Generate Global Config from Env Vars"
	For a user `user` on Linux, using the `uv tool` installation method, a `config.toml` generated with the help of an environment variable might look like:
	```
	$ BLEXT_PATH_GLOBAL_CACHE=/home/user/special-blext-cache blext show global_config
	[cfg]
	path_global_cache = "/home/user/special-blext-cache"
	path_blender_exe = "/home/user/.local/bin/blender"
	path_uv_exe = "/home/user/.local/share/uv/tools/blext/bin/uv"
	```
