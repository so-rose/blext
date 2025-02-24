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

"""Implements the `show init_settings` command."""

import typing as typ
from pathlib import Path

import pydantic as pyd

from blext import exceptions as exc
from blext import extyp, loaders

from ._context_show import APP_SHOW, CONSOLE


####################
# - Command: Show Spec
####################
@APP_SHOW.command(name='init_settings', group='Information')
def show_init_settings(
	proj: Path | None = None,
	*,
	platform: extyp.BLPlatform | typ.Literal['detect'] | None = None,
	profile: extyp.StandardReleaseProfile | str = 'release',
	format: typ.Literal['json', 'toml'] = 'toml',  # noqa: A002
) -> None:
	"""Print the complete extension specification.

	Parameters:
		bl_platform: The Blender platform to build the extension for.
		proj_path: Path to a `pyproject.toml` or a folder containing a `pyproject.toml`, which specifies the Blender extension.
		release_profile: The release profile to bake into the extension.
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

	# Show BLExtSpec
	CONSOLE.print(blext_spec.export_init_settings(fmt=format))
