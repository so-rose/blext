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

import typing as typ
from pathlib import Path

import pydantic as pyd
import rich.markdown
import rich.table

from blext import exceptions as exc
from blext import extyp, loaders

from ._context_show import APP_SHOW, CONSOLE


####################
# - Command: Show Spec
####################
@APP_SHOW.command(name='deps', group='Information')
def show_deps(
	proj: Path | None = None,
	*,
	platform: extyp.BLPlatform | typ.Literal['detect'] | None = None,
	profile: extyp.StandardReleaseProfile | str = 'release',
	sort_by: typ.Literal['filename', 'size'] = 'size',
	format: typ.Literal['table'] = 'table',  # noqa: A002
) -> None:
	"""Print the complete extension specification.

	Parameters:
		proj: Path to the Blender extension project.
		bl_platform: Blender platform(s) to constrain the extension to.
			Use "detect" to constrain to detect the current platform.
		release_profile: The release profile to apply to the extension.
		sort_by: How to sort the project dependencies table.
		format: The text format to show the project dependencies with.
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

	# Sort Wheels
	with exc.handle(exc.pretty, ValueError):
		blext_wheels = sorted(
			blext_spec.wheels_graph.wheels,
			key={
				'filename': lambda wheel: wheel.filename,
				'size': lambda wheel: wheel.sort_key_size,
			}[sort_by],
		)

	####################
	# - UI: Create Table w/Wheel Data
	####################
	if format == 'table':
		# Assemble Table of Wheels
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
				', '.join(list(wheel.python_tags))
				+ '|'
				+ ', '.join(list(wheel.abi_tags)),
				wheel.size.human_readable(decimal=True, separator=' ')
				if wheel.size is not None
				else 'Unknown',
			)
		table.add_section()
		table.add_row(
			f'={len(blext_spec.wheels_graph.wheels)} wheels',
			'',
			', '.join(blext_spec.bl_platforms),
			'',
			f'={blext_spec.wheels_graph.total_size_bytes.human_readable(decimal=True, separator=" ")}',
		)
		## TODO: A column that checks whether the wheel is downloaded/cached?
		## TODO: Export as ex.

		####################
		# - UI: Print
		####################
		CONSOLE.print(table)
