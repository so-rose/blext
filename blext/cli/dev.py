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

from pathlib import Path

from ._context import (
	APP,
	DEFAULT_BLEXT_INFO,
	DEFAULT_CONFIG,
	ParameterBLExtInfo,
	ParameterConfig,
)
from .run import run


@APP.command()
def dev(
	*,
	blext_info: ParameterBLExtInfo = DEFAULT_BLEXT_INFO,
	blend: Path | None = None,
	headless: bool = False,
	factory_startup: bool = True,
	config: ParameterConfig = DEFAULT_CONFIG,
) -> None:
	"""Run an extension live in Blender (w/`debug` profile).

	Parameters:
		proj: Path to Blender extension project.
		blend: `.blend` file to open after loading the extension.
		headless: Run Blender without the GUI.
		factory_startup: Run Blender with default "factory settings".
	"""
	blext_info = blext_info.model_copy(
		update={
			'profile': 'debug' if blext_info.profile is None else blext_info.platform,
		},
		deep=True,
	)
	run(
		blext_info=blext_info,
		blend=blend,
		headless=headless,
		factory_startup=factory_startup,
		config=config,
	)
