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

import typing as typ
from pathlib import Path

import pydantic as pyd

from blext import exceptions as exc
from blext import extyp, loaders

from ._context_show import APP_SHOW, CONSOLE


####################
# - Command: Show Spec
####################
@APP_SHOW.command(name='spec')
def show_spec(
	proj: Path | None = None,
	*,
	platform: extyp.BLPlatform | typ.Literal['detect'] | None = None,
	profile: extyp.StandardReleaseProfile | str = 'release',
	format: typ.Literal['raw'] = 'raw',  # noqa: A002
) -> None:
	"""[Show] complete extension specification.

	Parameters:
		proj: Path to Blender extension project.
		platform: Platform to build extension for.
			"detect" uses the current platform.
		profile: Initial settings to build extension with.
			Alters `initial_setings.toml` in the extension.
		sort_by: Column to sort dependencies by.
		format: Text format to output.
	"""
	# Parse BLExtSpec
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		blext_spec = loaders.load_bl_platform_into_spec(
			loaders.load_blext_spec(
				proj_uri=proj,
				release_profile_id=profile,
			),
			bl_platform_ref=platform,
		)

	# Show BLExtSpec
	if format == 'raw':
		CONSOLE.print(blext_spec)

	## TODO: Can we strategically truncate the BLExtWheel? Is that a good idea? Maybe a CLI option that selects certain elements of the specification to truncate?
