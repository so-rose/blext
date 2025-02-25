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

"""Implements the `dev` command."""

import tempfile
from pathlib import Path

import blext.exceptions as exc
from blext import blender, finders

from ._context import APP, CONSOLE
from .build import build


@APP.command()
def dev(
	proj: Path | None = None,
	*,
	blend: Path | None = None,
	headless: bool = False,
	factory_startup: bool = True,
) -> None:
	"""Launch the extension locally, using Blender.

	Parameters:
		proj: Path to the Blender extension project.
		bl_platform: Blender platform(s) to constrain the extension to.
			Use "detect" to constrain to detect the current platform.
		release_profile: The release profile to apply to the extension.
		format: The text format to show the Blender manifest as.
	"""
	with exc.handle(exc.pretty, ValueError):
		blender_exe = finders.find_blender_exe()

	with tempfile.TemporaryDirectory() as tmp_build_dir:
		path_zip = Path(tmp_build_dir) / 'blext-dev-extension.zip'

		####################
		# - Build Extension
		####################
		build(
			proj,
			platform='detect',
			profile='dev',
			output=path_zip,
			overwrite=True,
			vendor=True,
		)

		####################
		# - Run Extension in Blender
		####################
		CONSOLE.print()
		CONSOLE.rule('[bold]Running Extension w/Blender[/bold]')
		blender.run_extension(
			blender_exe,
			path_zip=path_zip,
			headless=headless,
			path_blend=blend,
		)
