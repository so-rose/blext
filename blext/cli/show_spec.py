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

"""Implements the `show spec` command."""

from pathlib import Path

from blext import supported

from ._context_show import APP_SHOW, CONSOLE
from ._parse import parse_bl_platform, parse_blext_spec


####################
# - Command: Show Spec
####################
@APP_SHOW.command(name='spec', group='Information')
def show_spec(
	proj_path: Path | None = None,
	bl_platform: supported.BLPlatform | None = None,
	release_profile: supported.ReleaseProfile = supported.ReleaseProfile.Release,
) -> None:
	"""Print the complete extension specification.

	Parameters:
		bl_platform: The Blender platform to build the extension for.
		proj_path: Path to a `pyproject.toml` or a folder containing a `pyproject.toml`, which specifies the Blender extension.
		release_profile: The release profile to bake into the extension.
	"""
	# Parse CLI
	blext_spec = parse_blext_spec(
		proj_path=proj_path,
		release_profile=release_profile,
	)
	bl_platform = parse_bl_platform(
		blext_spec,
		bl_platform_hint=bl_platform,
		detect=True,
	)

	# Show BLExtSpec
	CONSOLE.print(blext_spec)
