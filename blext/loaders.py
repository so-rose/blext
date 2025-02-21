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

"""Load various data from external sources."""

import base64
import hashlib
import typing as typ
from pathlib import Path

from . import extyp, finders, paths, spec

HASH_ALGO_SCRIPTPATH = 'sha256'


def load_blext_spec(
	proj_uri: Path | None = None,
	*,
	release_profile_id: extyp.StandardReleaseProfile | str = 'release',
) -> spec.BLExtSpec:
	"""Parse a `BLExtSpec` from a specified project path and release profile.

	Parameters:
		proj_path: The path to a Blender extension project.

			- When a `pyproject.toml` file is given, it will be used as the project settings.
			- When a directory is given, it must contain a `pyproject.toml` file.
			- When a `.py` script is given, it must contain metadata in its header per the [inline script metadata specification](https://packaging.python.org/en/latest/specifications/inline-script-metadata/).

		proj_path: A release profile

	Returns:
		A specification of the Blender extension, which can be used to package it.

	Raises:
		ValueError: When
	"""
	path_proj_spec = finders.find_proj_spec(proj_uri)
	blext_spec = spec.BLExtSpec.from_proj_spec_path(
		path_proj_spec=path_proj_spec,
		release_profile_id=release_profile_id,
	)

	# Register BLExtSpec -> Project Root Path
	## - Script BLExt: Use Global Spec Cache for "Project" Root Directory
	## - Project BLExt: Use Project Spec Cache for "Project" Root Directory
	if path_proj_spec.name.endswith('.py'):
		hasher = hashlib.new(HASH_ALGO_SCRIPTPATH)
		hasher.update(str(path_proj_spec).encode())
		unique_script_id = base64.b64encode(hasher.digest(), altchars=b'+-').decode(
			'utf-8'
		)[:-1]  ## Slice to chop off the = at the end.

		path_root = paths.PATH_GLOBAL_SCRIPT_CACHE / unique_script_id
		path_root.mkdir(exist_ok=True)
		paths.register_blext_spec(
			blext_spec,
			path_root=path_root,
			path_script_source=path_proj_spec,
		)
	else:
		paths.register_blext_spec(blext_spec, path_root=path_proj_spec.parent)

	return blext_spec


def load_bl_platform_into_spec(
	blext_spec: spec.BLExtSpec,
	*,
	bl_platform_ref: frozenset[extyp.BLPlatform]
	| extyp.BLPlatform
	| typ.Literal['detect']
	| None = None,
) -> spec.BLExtSpec:
	"""Constrain the Blender platforms supported by a Blender extension.

	Parameters:
		blext_spec: The path to a Blender extension project.

			- When a `pyproject.toml` file is given, it will be used as the project settings.
			- When a directory is given, it must contain a `pyproject.toml` file.
			- When a `.py` script is given, it must contain metadata in its header per the [inline script metadata specification](https://packaging.python.org/en/latest/specifications/inline-script-metadata/).

		proj_path: A release profile

	Returns:
		A specification of the Blender extension, which can be used to package it.

	Raises:
		ValueError: When either no platform could be selected, or the selected platform is not supported by the extension.
	"""
	match bl_platform_ref:
		case None:
			return blext_spec

		case 'detect':
			new_blext_spec = blext_spec.constrain_to_bl_platform(
				finders.detect_local_blplatform()
			)

		case extyp.BLPlatform():
			new_blext_spec = blext_spec.constrain_to_bl_platform(bl_platform_ref)

		case frozenset():
			new_blext_spec = blext_spec.constrain_to_bl_platform(bl_platform_ref)

	# Update BLExtSpec -> Project Root Path Registration
	## - Constraining the BLExtSpec has changed them.
	## - Therefore, for there to still be a path registered for the specification, the registration must be updated.
	paths.update_registered_blext_spec(blext_spec, new_blext_spec)

	return new_blext_spec
