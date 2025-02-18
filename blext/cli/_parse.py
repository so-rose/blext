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

from pathlib import Path

import pydantic as pyd

import blext.exceptions as exc
from blext import finders, spec, supported


def parse_blext_spec(
	*,
	proj_path: Path | None = None,
	release_profile: supported.ReleaseProfile = supported.ReleaseProfile.Release,
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
	# Parse CLI
	with exc.handle(exc.pretty, ValueError):
		path_proj_spec = finders.find_proj_spec(proj_path)

	# Parse Blender Extension Specification
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		return spec.BLExtSpec.from_proj_spec(
			path_proj_spec=path_proj_spec,
			release_profile=release_profile,
		)


def parse_bl_platform(
	blext_spec: spec.BLExtSpec,
	*,
	bl_platform_hint: supported.BLPlatform | None = None,
	detect: bool = True,
) -> supported.BLPlatform:
	"""Deduce the platform for which build the extension for.

	To specify a particular Blender platform to use, the following sequence of possibilities are tried (in order):

		1. If `bl_platform_hint` is given, then it will be selected.
		2. If `detect` is given, then the local Blender platform will be detected and selected.
		3. Otherwise, an error will be thrown.

	**The selected platform must always be compatible with `blext_spec`.**
	This is also checked automatically.

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
	if bl_platform_hint is not None:
		## TODO: Suport checking extension support.
		return bl_platform_hint

	if bl_platform_hint is None and detect:
		with exc.handle(exc.pretty, ValueError):
			return finders.detect_local_blplatform()

	with exc.handle(exc.pretty, ValueError):
		msg = 'Tried to find a Blender platform, but no hint was given, and auto-detection was disallowed'
		raise ValueError(msg)
