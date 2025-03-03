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

"""Implements `blext show deps`."""

import typing as typ

import pydantic as pyd
import rich.markdown
import rich.table

from blext import exceptions as exc

from ._context import (
	DEFAULT_BLEXT_INFO,
	DEFAULT_CONFIG,
	ParameterBLExtInfo,
	ParameterConfig,
)
from ._context_show import APP_SHOW, CONSOLE


####################
# - Command: Show Spec
####################
@APP_SHOW.command(name='deps')
def show_deps(
	*,
	blext_info: ParameterBLExtInfo = DEFAULT_BLEXT_INFO,
	sort_by: typ.Literal['filename', 'size'] = 'filename',
	format: typ.Literal['table'] = 'table',  # noqa: A002
	config: ParameterConfig = DEFAULT_CONFIG,
) -> None:
	"""Inspect all Python dependencies.

	Parameters:
		proj: Path to Blender extension project.
		platform: Platform to build extension for.
			"detect" uses the current platform.
		profile: Initial settings to build extension with.
			Alters `initial_setings.toml` in the extension.
		sort_by: Column to sort dependencies by.
		format: Text format to output.
	"""
	# Parse CLI
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		blext_spec = blext_info.blext_spec(config)

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
		## TODO: Export as csv

		####################
		# - UI: Print
		####################
		CONSOLE.print(table)
