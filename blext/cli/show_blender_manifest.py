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

"""Implements the `show blender_manifest` command."""

import typing as typ
from pathlib import Path

import pydantic as pyd

from blext import exceptions as exc
from blext import extyp, loaders

from ._context_show import APP_SHOW, CONSOLE


####################
# - Command: Show Spec
####################
@APP_SHOW.command(name='blender_manifest', group='Information')
def show_blender_manifest(
	proj: Path | None = None,
	*,
	platform: extyp.BLPlatform | typ.Literal['detect'] | None = None,
	profile: extyp.StandardReleaseProfile | str = 'release',
	format: typ.Literal['json', 'toml'] = 'toml',  # noqa: A002
) -> None:
	"""Print the complete extension specification.

	Parameters:
		proj: Path to the Blender extension project.
		platform: Blender platform(s) to constrain the extension to.
			Use "detect" to constrain to detect the current platform.
		release_profile: The release profile to apply to the extension.
		format: The text format to show the Blender manifest as.
	"""
	# Parse CLI
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		blext_spec = loaders.load_bl_platform_into_spec(
			loaders.load_blext_spec(
				proj_uri=proj,
				release_profile_id=profile,
			),
			bl_platform_ref=platform,
		)

	# Show Blender Manifest
	CONSOLE.print(blext_spec.export_blender_manifest(fmt=format))
