# Script Extensions
You can make a complete Blender extension, _including Python dependencies_, in just one `.py` file!

In `blext`, these are called "script extensions" to differentiate them from "project extensions".

!!! example
	This is a **fully functional** script extension:
	```python
	# /// script
	# requires-python = "==3.11"
	# dependencies = [
	#   "scipy==1.15.2",
	# ]
	#
	# [project]
	# name = "single_file_ext"
	# version = "0.1.0"
	# description = "A quick example of a one-file Blender w/Python dependencies"
	# authors = [
	#     { name = "John Doe", email = "jdoe@example.com" },
	# ]
	# license = { text = "AGPL-3.0-or-later" }
	#
	# [tool.blext]
	# pretty_name = "Single File Extension Example"
	# blender_version_min = '4.3'
	# bl_tags = ["Development"]
	# copyright = ["2025 blext Contributors"]
	#
	# supported_platforms = [
	# 	'windows-x64',
	# 	'macos-arm64',
	# 	'linux-x64',
	# ]
	# ///
	import bpy
	import numpy as np
	import scipy as sc


	####################
	# - Simple Operator
	####################
	class SimpleOperator(bpy.types.Operator):
		"""Operator that shows a message."""

		bl_idname = f'single_file_ext.simple_operator'
		bl_label = 'Simple Operator'

		@classmethod
		def poll(cls, _: bpy.types.Context) -> bool:
			"""Always allow operator to run."""
			return True

		def execute(self, _: bpy.types.Context) -> set[str]:
			"""Display a simple message on execution."""
			self.report(
				{'INFO'},
				(
					f'sc.constants.speed_of_light={sc.constants.speed_of_light}'
					f'np.__version__={np.__version__}'
				),
			)

			return {'FINISHED'}


	####################
	# - Menus
	####################
	def menu_func(self, context):
		self.layout.operator(SimpleOperator.bl_idname, text=SimpleOperator.bl_label)


	####################
	# - Registration
	####################
	def register() -> None:
		bpy.utils.register_class(SimpleOperator)
		bpy.types.VIEW3D_MT_object.append(menu_func)


	def unregister() -> None:
		bpy.utils.unregister_class(SimpleOperator)
		bpy.types.VIEW3D_MT_object.remove(menu_func)
	```



## Differences w/Project Extensions
In general, all [CLI / Commands](cli/commands.md) work the same, with notable minor differences.

!!! example "Create a Script Extension"
	```
	blext init script-ext.py
	```

	_This creates a new script extension named `script-ext.py`._

!!! example "Build a Script Extension"
	```
	blext build script-ext.py
	```

	_This builds the script extension named `script-ext.py`, to a zipfile in the same folder._



### Explicit Location
Script extensions must be **explicitly** located.

!!! example
	Say you want to run a script extension named `extension.py`.

	**Invalid**: Implicit search for an extension.
	```
	$ blext run
	ValueError:
	    No Blender extension could be found in the current directory ".".
	```

	**Valid**: Explicitly specifying the script.
	```
	$ blext run extension.py
	...  # It works!
	```


!!! example "Run a Remote Script Extension"
	```
	blext run script+https://example.com/path/to/script-ext.py
	```

	_This downloads and runs a script extension from the URL `https://example.com/path/to/script-ext.py`._



### Config Field Placement
!!! note
	The standardized script equivalent to `pyproject.toml` is a `# /// script` header.

	See [Configuring: Inline Metadata][configuring-inline-metadata] for more details.

There are **two fields** with different placements than in the `pyproject.toml` of a project extension:

- `requires-python`: Must be defined top-level, instead of in the `[project]` table.
- `dependencies`: Must be defined top-level, instead of in the `[project]` table.


!!! example
	**Invalid**: Placing everything under `[project]`, like in `pyproject.toml`.
	```python
	# /// script
	# [project]
	# name = "script_ext"
	# version = "0.1.0"
	# requires-python = "==3.11"
	# dependencies = [
	#   "scipy==1.15.2",
	# ]
	# ...
	# ///
	```

	**Valid**: Top-level `requires-python` and `dependencies`.
	```python
	# /// script
	# requires-python = "==3.11"
	# dependencies = [
	#   "scipy==1.15.2",
	# ]
	#
	# [project]
	# name = "script_ext"
	# version = "0.1.0"
	# ...
	# ///
	```



### Adding PyPi Dependencies
Once again, the `uv` package manager saves the day.

To add a PyPi dependency to a script extension, just run:
```
uv add --script single-file-ext.py scipy
```

!!! question "What if `blext` was installed without `uv`?"
	`blext` ships with `uv` as a dependency, and provides a convenient alias to this internal version.

	You can therefore always type:
	```
	blext uv add --script single-file-ext.py scipy
	```



### Build Artifacts
When building a script extension, there are **two differences** in where the results of that build process end up:

- **Sidecar `.py.lock`**: Just like project extensions lock their dependencies to a `uv.lock` file, a script extension locks its dependencies to a `<extname>.py.lock`.

- **Default `.zip` Location**: By default, the zipfile builds to an auto-generated name, in the same folder as the `.py` script extension.
	- `--output | -o`: As usual, this lets you 

!!! example "Build Script Extension to Named Zipfile"
	```
	$ blext build script-ext.py -o my-extension.zip
	```
	
	_This builds the script extension `script-ext.py` to the zipfile `my-extension.zip`._

!!! note
	Currently, the location of the `.py.lock` file cannot be changed.
	This requires the folder containing the script to be writable.

	If you need support for read-only script-extension parent directories, please open an Issue.



## Configuring: Inline Metadata
Script extensions are configured using _almost_ the same fields and syntax as `pyproject.toml`.

Difference is, these fields live in a `# /// script` header of the file.

!!! note "Scipt Extension Configuration: Fields and Syntax"
	There are **exactly two** differences in fields and syntax, compared to project extensions.

	- See [Project Extensions](project_extensions.md) for more on valid fields and syntax.
	- See [Differences w/Project Extensions / Configuration][configuration] for more on the two differences.

!!! example
	This is an example of a valid header for a script extension:
	```python
	# /// script
	# requires-python = "==3.11"
	# dependencies = [
	#   "scipy==1.15.2",
	# ]
	#
	# [project]
	# name = "single_file_ext"
	# version = "0.1.0"
	# description = "A quick example of a one-file Blender w/Python dependencies"
	# authors = [
	#     { name = "John Doe", email = "jdoe@example.com" },
	# ]
	# license = { text = "AGPL-3.0-or-later" }
	#
	# [tool.blext]
	# pretty_name = "Single File Extension Example"
	# blender_version_min = '4.3'
	# bl_tags = ["Development"]
	# copyright = ["2025 blext Contributors"]
	#
	# supported_platforms = [
	# 	'windows-x64',
	# 	'macos-arm64',
	# 	'linux-x64',
	# ]
	# ///
	```

!!! info
	The format of this special header is an official Python standard called [inline script metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata).

	Strictly speaking, for `blext` to expect a `[project]` table in the `/// script` tag means that this is not **quite** standard-compliant "inline script metadata", since any other non-`[tool]` table is forbitten.

	Unifying script and project extensions in a clear way was determined to be more important.
