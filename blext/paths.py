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

"""Weakly linked mapping from extension project specification to relevant paths."""

from pathlib import Path

import platformdirs

from . import spec

####################
# - Constants
####################
PATH_GLOBAL_CACHE = Path(platformdirs.user_cache_dir('blext', 'blext'))
PATH_GLOBAL_CACHE.mkdir(exist_ok=True)

PATH_GLOBAL_SCRIPT_CACHE = PATH_GLOBAL_CACHE / 'script_cache'
PATH_GLOBAL_SCRIPT_CACHE.mkdir(exist_ok=True)


## TODO: Use a blext configuration file.


####################
# - Globals
####################
_SPEC_ROOT_PATHS: dict[spec.BLExtSpec, Path] = {}
_SCRIPT_SOURCE_PATHS: dict[spec.BLExtSpec, Path] = {}


def register_blext_spec(
	blext_spec: spec.BLExtSpec,
	*,
	path_root: Path,
	path_script_source: Path | None = None,
) -> None:
	_SPEC_ROOT_PATHS[blext_spec] = path_root
	if path_script_source is not None:
		_SCRIPT_SOURCE_PATHS[blext_spec] = path_script_source.resolve()


def update_registered_blext_spec(
	old_blext_spec: spec.BLExtSpec, new_blext_spec: spec.BLExtSpec
) -> None:
	_SPEC_ROOT_PATHS[new_blext_spec] = _SPEC_ROOT_PATHS.pop(old_blext_spec)
	if old_blext_spec in _SCRIPT_SOURCE_PATHS:
		_SCRIPT_SOURCE_PATHS[new_blext_spec] = _SCRIPT_SOURCE_PATHS.pop(old_blext_spec)


####################
# - Root Path
####################
def path_root(blext_spec: spec.BLExtSpec) -> Path:
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
	if path_root(blext_spec).is_relative_to(PATH_GLOBAL_SCRIPT_CACHE):
		return path_root(blext_spec)

	path_dev = path_root(blext_spec) / '.dev'
	path_dev.mkdir(exist_ok=True)
	return path_dev


def path_wheels(blext_spec: spec.BLExtSpec) -> Path:
	"""Path to the project's downloaded wheels."""
	path_wheels = path_dev(blext_spec) / 'wheels'
	path_wheels.mkdir(exist_ok=True)
	return path_wheels


def path_prepack(blext_spec: spec.BLExtSpec) -> Path:
	"""Path to the project's prepack folder, where pre-packed `.zip`s are written to."""
	path_prepack = path_dev(blext_spec) / 'prepack'
	path_prepack.mkdir(exist_ok=True)
	return path_prepack


def path_build(blext_spec: spec.BLExtSpec) -> Path:
	"""Path to the project's build folder, where extension `.zip`s are written to."""
	path_build = path_dev(blext_spec) / 'build'
	path_build.mkdir(exist_ok=True)
	return path_build


def path_local(blext_spec: spec.BLExtSpec) -> Path:
	"""Path to the project's build folder, where extension `.zip`s are written to."""
	path_local = path_dev(blext_spec) / 'local'
	path_local.mkdir(exist_ok=True)
	return path_local


####################
# - Python Paths
####################
def path_pypkg(blext_spec: spec.BLExtSpec) -> Path | None:
	"""Path to the Python package of the extension.

	Returns:
		None if the extension is a script extension.
		Otherwise, the root path of the extension's Python package.
	"""
	if blext_spec in _SCRIPT_SOURCE_PATHS:
		return None

	return path_root(blext_spec) / blext_spec.id


def path_pysrc(blext_spec: spec.BLExtSpec) -> Path | None:
	"""Path to the Python package of the extension.

	Returns:
		None if the extension is a script extension.
		Otherwise, the root path of the extension's Python package.
	"""
	if blext_spec in _SCRIPT_SOURCE_PATHS:
		return _SCRIPT_SOURCE_PATHS[blext_spec]

	return None


def path_uv_lock(blext_spec: spec.BLExtSpec) -> Path:
	"""Path to the Python package of the extension.

	Returns:
		None if the extension is a script extension.
		Otherwise, the root path of the extension's Python package.
	"""
	if blext_spec in _SCRIPT_SOURCE_PATHS:
		return path_root(blext_spec).parent / (path_root(blext_spec).name + '.lock')
	return path_root(blext_spec) / 'uv.lock'
