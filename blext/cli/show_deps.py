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

"""Implements the `show deps` command."""

from pathlib import Path

import pydantic as pyd
import rich.markdown
import rich.table

from blext import exceptions as exc
from blext import supported, wheels

from ._context_show import APP_SHOW, CONSOLE
from ._parse import parse_bl_platform, parse_blext_spec


####################
# - Command: Show Spec
####################
@APP_SHOW.command(name='deps', group='Information')
def show_deps(
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
	if bl_platform is not None:
		bl_platform = parse_bl_platform(
			blext_spec,
			bl_platform_hint=bl_platform,
			detect=False,
		)
		blext_spec = blext_spec.constrain_to_bl_platform(bl_platform)

	# Show BLExtSpec
	with exc.handle(exc.pretty, ValueError):
		blext_wheels: list[wheels.BLExtWheel] = sorted(
			blext_spec.wheels, key=lambda el: int(el.size) if el.size is not None else 0
		)

	byte_size = pyd.ByteSize(
		sum(int(wheel.size) if wheel.size is not None else 0 for wheel in blext_wheels)
	)

	table = rich.table.Table()
	table.add_column('Name')
	table.add_column('Version', no_wrap=True)
	table.add_column('Platforms')
	table.add_column('Py|ABI', no_wrap=True)
	table.add_column('Size', no_wrap=True)

	for wheel in blext_wheels:
		table.add_row(
			wheel.project,
			wheel.version,
			', '.join(list(wheel.platform_tags)),
			', '.join(list(wheel.python_tags)) + '|' + ', '.join(list(wheel.abi_tags)),
			wheel.size.human_readable(decimal=True, separator=' ')
			if wheel.size is not None
			else 'Unknown',
		)
	table.add_section()
	table.add_row(
		f'={len(blext_spec.wheels)} wheels',
		'',
		', '.join(blext_spec.bl_platforms),
		'',
		f'={byte_size.human_readable(decimal=True, separator=" ")}',
	)

	CONSOLE.print(table)
