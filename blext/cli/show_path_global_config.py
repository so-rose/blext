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

"""Implements `show path global_config`."""

from blext import ui

from ._context_show_path import APP_SHOW_PATH, CONSOLE


####################
# - Command: Show Spec
####################
@APP_SHOW_PATH.command(name='global_config')
def show_path_global_config() -> None:
	"""Path to the global configuration file used by `blext`."""
	CONSOLE.print(ui.PATH_GLOBAL_CONFIG)
