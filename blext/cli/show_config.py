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

"""Implements `blext show config`."""

import typing as typ

from ._context import (
	DEFAULT_CONFIG,
	ParameterConfig,
)
from ._context_show import APP_SHOW, CONSOLE


####################
# - Command: Show Spec
####################
@APP_SHOW.command(name='config')
def show_config(
	*,
	format: typ.Literal['raw', 'json', 'toml'] = 'toml',  # noqa: A002
	config: ParameterConfig = DEFAULT_CONFIG,
) -> None:
	"""Inspect all Python dependencies.

	Parameters:
		format: Column to sort dependencies by.
		config: Global configuration overrides.
	"""
	if format == 'raw':
		CONSOLE.print(config)
	else:
		CONSOLE.print(config.export_config(fmt=format), markup=False, end='')
