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
PATH_GLOBAL_SPEC_CACHE = Path(platformdirs.user_cache_dir('blext', 'blext'))

## TODO: Use a blext configuration file.


####################
# - Globals
####################
_BLEXT_SPEC_PATHS: dict[spec.BLExtSpec, Path] = {}


####################
# - Registration and Retrieval
####################
def register_blext_spec(blext_spec: spec.BLExtSpec, path_root: Path) -> None:
	_BLEXT_SPEC_PATHS[blext_spec] = path_root


def path_root(blext_spec: spec.BLExtSpec) -> Path:
	path_root = _BLEXT_SPEC_PATHS.get(blext_spec, None)
	if path_root is not None:
		return path_root

	msg = 'Tried to find root path for a passed BLExtSpec, but it has none registered. This should not happen.'
	raise RuntimeError(msg)


####################
# - .dev Paths
####################
def path_dev(blext_spec: spec.BLExtSpec) -> Path:
	"""Path to the project `.dev/` folder.

	Notes:
		`.dev` should NOT be checked into version control systems.

	"""
	path_dev = path_root(blext_spec) / '.dev'
	path_dev.mkdir(exist_ok=True)
	return path_dev


def path_pypkg(blext_spec: spec.BLExtSpec) -> Path:
	"""Path to the Python package of the extension."""
	return path_root(blext_spec) / blext_spec.id


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
