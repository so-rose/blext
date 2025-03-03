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

"""Implements `blext dev`."""

import tempfile
from pathlib import Path

import blext.exceptions as exc
from blext import blender, finders

from ._context import (
	APP,
	CONSOLE,
	DEFAULT_BLEXT_INFO,
	DEFAULT_CONFIG,
	ParameterBLExtInfo,
	ParameterConfig,
)
from .build import build


@APP.command()
def run(
	*,
	blext_info: ParameterBLExtInfo = DEFAULT_BLEXT_INFO,
	blend: Path | None = None,
	headless: bool = False,
	factory_startup: bool = True,
	config: ParameterConfig = DEFAULT_CONFIG,
) -> None:
	"""Run an extension live in Blender.

	Parameters:
		proj: Path to Blender extension project.
		blend: `.blend` file to open after loading the extension.
		headless: Run Blender without the GUI.
		factory_startup: Run Blender with default "factory settings".
	"""
	with exc.handle(exc.pretty, ValueError):
		blender_exe = finders.find_blender_exe(
			override_path_blender_exe=config.path_blender_exe
		)

	blext_info = blext_info.model_copy(
		update={
			'platform': (
				('detect',) if blext_info.platform == () else blext_info.platform
			),
		},
		deep=True,
	)
	with tempfile.TemporaryDirectory() as tmp_build_dir:
		path_zip = Path(tmp_build_dir) / 'blext-dev-extension.zip'

		####################
		# - Build Extension
		####################
		build(
			blext_info=blext_info,
			output=path_zip,
			overwrite=True,
			vendor=True,
			config=config,
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
			factory_startup=factory_startup,
			path_blend=blend,
		)
