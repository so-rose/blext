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

"""Implements the `show manifest` command."""

from blext import exceptions as exc
from blext import finders

from ._context_show_path import APP_SHOW_PATH, CONSOLE


####################
# - Command: Show Spec
####################
@APP_SHOW_PATH.command(name='blender', group='Information')
def show_path_blender() -> None:
	"""Print the complete extension specification.

	Parameters:
		bl_platform: The Blender platform to build the extension for.
		proj_path: Path to a `pyproject.toml` or a folder containing a `pyproject.toml`, which specifies the Blender extension.
		release_profile: The release profile to bake into the extension.
	"""
	# Show Found Blender EXE
	with exc.handle(exc.pretty, ValueError):
		blender_exe = finders.find_blender_exe()

	CONSOLE.print(blender_exe)
