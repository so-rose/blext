# blext
# Copyright (C) 2025 blext Project Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Mapping between extension project specifications, and paths to use for various purposes.

Attributes:
	_SPEC_ROOT_PATHS: Mapping from each extension specs to their "root path".
		**By definition**, a "root path" is a writable directory used by `blext` for project-specific file operations.
		In particular, it doesn't need to contain project source code (though this is often convenient).
		It also doesn't need to persist between runs of `blext`.
	_SCRIPT_SOURCE_PATHS: Mapping from each script-extension spec, to the corresponding "root path".
		**By definition**, a spec is a "script extension" if it is a key of this dictionary.
"""

import os
from pathlib import Path

from . import config, spec

####################
# - Globals
####################
_SPEC_ROOT_PATHS: dict[spec.BLExtSpec, Path] = {}
_SCRIPT_SOURCE_PATHS: dict[spec.BLExtSpec, Path] = {}


####################
# - Globals Interaction
####################
def register_blext_spec(
	blext_spec: spec.BLExtSpec,
	*,
	path_root: Path,
	path_script_source: Path | None = None,
) -> None:
	"""Register a global mapping from an extension spec, to where it was found.

	When loading an extension specification, the path it was found should be registered using this function.

	Notes:
		Extension specifications are portable descriptions of an extension.
		It would not, therefore, be appropriate to keep information about where that specification was found on _this particular_ computer, since that information is not portable.

	Parameters
		blext_spec: Extension specification to register a path mapping for.
		path_root: Root directory of the Blender extension project.
			For scripts, this should be set to a globally-writable cache path.
		path_script_source: For script extensions, this is the path to the script source code.
	"""
	# Set Root Path IF
	## - Is Directory: Obviously.
	## - Is Readable and Writable: So it can be used as it needs to be used.
	if path_root.is_dir():
		if os.access(path_root, os.R_OK):
			if os.access(path_root, os.W_OK):
				_SPEC_ROOT_PATHS[blext_spec] = path_root.resolve()
			else:
				msg = f'Tried to register root path {path_root}, but is not writable. Please grant `blext` permission to write this folder.'
				raise ValueError(msg)
		else:
			msg = f'Tried to register root path {path_root}, but is not readable. Please grant `blext` permission to read this folder.'
			raise ValueError(msg)
	else:
		msg = f'Tried to register root path {path_root}, but is not a folder. Please review the loader logic.'
		raise ValueError(msg)

	# Set Script Source Path IF Readable
	if path_script_source is not None:
		_SCRIPT_SOURCE_PATHS[blext_spec] = path_script_source.resolve()


def update_registered_blext_spec(
	old_blext_spec: spec.BLExtSpec, new_blext_spec: spec.BLExtSpec
) -> None:
	"""Replace an old extension spec with a new one, without altering the paths.

	This should be called when constraining a spec's supported `BLPlatform`s, since this creates a new specification.

	Parameters
		old_blext_spec: The specification that is to be altered.
		new_blext_spec: The specification that replaces the old specification.
	"""
	_SPEC_ROOT_PATHS[new_blext_spec] = _SPEC_ROOT_PATHS.pop(old_blext_spec)
	if old_blext_spec in _SCRIPT_SOURCE_PATHS:
		_SCRIPT_SOURCE_PATHS[new_blext_spec] = _SCRIPT_SOURCE_PATHS.pop(old_blext_spec)


####################
# - Root Path
####################
def path_root(blext_spec: spec.BLExtSpec) -> Path:
	"""The project's root folder.

	**By definition**, a "root path" is a writable directory used by `blext` for project-specific file operations.

	Notes:
		- A "root path" **does** need to be writable.
		- A "root path" **does not** need to contain project source code (though this is often convenient).
		It also doesn't need to persist between runs of `blext`.

	Warnings:
		The folder **must** support the creation of a `.dev/` subfolder.

	Notes:
		For script extensions, this should be a global cache path unique to that script.
	"""
	path_root = _SPEC_ROOT_PATHS.get(blext_spec)
	if path_root is not None:
		## TODO: Write an access-time to the cache, to help with auto-pruning cache entries that are no longer in use.
		return path_root

	msg = 'Tried to find root path for a passed BLExtSpec, but it has none registered. This should not happen.'
	raise RuntimeError(msg)


####################
# - .dev Paths
####################
def path_dev(blext_spec: spec.BLExtSpec) -> Path:
	"""Path to the project `.dev/` folder.

	When the root path is a subdirectory of `PATH_GLOBAL_SCRIPT_CACHE`, then this is the same as the project root path.

	Notes:
		`.dev` should NOT be checked into version control systems.

	"""
	if path_root(blext_spec).is_relative_to(config.CONFIG.path_global_script_cache):
		return path_root(blext_spec)

	path_dev = path_root(blext_spec) / '.dev'
	path_dev.mkdir(exist_ok=True)
	return path_dev


def path_wheels(blext_spec: spec.BLExtSpec) -> Path:
	"""Path to the project's wheel download cache."""
	path_wheels = path_dev(blext_spec) / 'wheels'
	path_wheels.mkdir(exist_ok=True)
	return path_wheels
	## TODO: Ideally, we can do cache management of wheels:
	## - A global cache could keep all wheels downloaded as part of `blext`'s operation.
	## - Each project could then request wheels from the global cache.
	## - If the global cache doesn't have the wheel, it would download.
	## - Once the global cache is hydrated, it would then hard-link wheels into the project cache.
	## - Any blext project could, in the course of using this cache, report what it needed.
	## - In this way, the global cache would be prunable without consequences.
	## - Note that any user-global cache introduces a schema-versioning problem. Be careful.


def path_prepack(blext_spec: spec.BLExtSpec) -> Path:
	"""Path to the project's prepack folder, where pre-packed `.zip`s are written to."""
	path_prepack = path_dev(blext_spec) / 'prepack'
	path_prepack.mkdir(exist_ok=True)
	return path_prepack


def path_build(blext_spec: spec.BLExtSpec) -> Path:
	"""Folder to place any `.zip`s are written to.

	Notes:

	For script extensions, the build folder is the folder containing the script.
	"""
	if blext_spec in _SCRIPT_SOURCE_PATHS:
		return _SCRIPT_SOURCE_PATHS[blext_spec].parent

	path_build = path_dev(blext_spec) / 'build'
	path_build.mkdir(exist_ok=True)
	return path_build


####################
# - Python Paths
####################
def path_pypkg(blext_spec: spec.BLExtSpec) -> Path | None:
	"""Root folder for a project extension's Python package.

	Notes:
		- It should be considered guaranteed that this path always contains a `pyproject.toml`.
		- **Remember** that an extension spec is a "project extension" iff it is **not** a key of `_SCRIPT_SOURCE_PATHS`.

	Returns:
		- `None`: If the extension is a script extension.
		- Else: Path to the root folder of the extension project.
	"""
	if blext_spec in _SCRIPT_SOURCE_PATHS:
		return None

	return path_root(blext_spec) / blext_spec.id


def path_pysrc(blext_spec: spec.BLExtSpec) -> Path | None:
	"""Source code path for a script extension.

	Notes:
		- It should be considered guaranteed that this path always ends with `.py`.
		- **Remember** that an extension spec is a "script extension" iff it is a key of `_SCRIPT_SOURCE_PATHS`.

	Returns:
		- `None`: If the extension is **not** a script extension.
		- Else: Path to the source code of the script extension.
	"""
	if blext_spec in _SCRIPT_SOURCE_PATHS:
		return _SCRIPT_SOURCE_PATHS[blext_spec]

	return None


def path_uv_lock(blext_spec: spec.BLExtSpec) -> Path:
	"""The `uv.lock` file for the given specification.

	Returns:
		None if the extension is a script extension.
		Otherwise, the root path of the extension's Python package.
	"""
	if blext_spec in _SCRIPT_SOURCE_PATHS:
		return _SCRIPT_SOURCE_PATHS[blext_spec].parent / (
			_SCRIPT_SOURCE_PATHS[blext_spec].name + '.lock'
		)
	return path_root(blext_spec) / 'uv.lock'
	## TODO: We really should run pydeps.uv.update_uv_lock(path_uv_lock) to make sure it exists.
