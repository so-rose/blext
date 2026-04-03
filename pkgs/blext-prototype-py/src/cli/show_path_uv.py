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

"""Implements `blext show path uv`."""

from ._context import (
	DEFAULT_CONFIG,
	ParameterConfig,
)
from ._context_show_path import APP_SHOW_PATH, CONSOLE


####################
# - Command: Show Spec
####################
@APP_SHOW_PATH.command(name='uv')
def show_path_uv(
	*,
	global_config: ParameterConfig = DEFAULT_CONFIG,
) -> None:
	"""Path to `uv` executable used by `blext`."""
	CONSOLE.print(global_config.path_uv_exe)
