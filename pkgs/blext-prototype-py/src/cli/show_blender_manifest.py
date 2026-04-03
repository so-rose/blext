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

"""Implements `blext show blender_manifest`."""

import typing as typ

from ._context import (
	DEFAULT_BLEXT_INFO,
	DEFAULT_CONFIG,
	ParameterBLExtInfo,
	ParameterConfig,
	ParameterProj,
)
from ._context_show import APP_SHOW, CONSOLE


####################
# - Command: Show Spec
####################
@APP_SHOW.command(name='blender_manifest')
def show_blender_manifest(
	proj: ParameterProj = None,
	*,
	blext_info: ParameterBLExtInfo = DEFAULT_BLEXT_INFO,
	global_config: ParameterConfig = DEFAULT_CONFIG,
	format: typ.Literal['json', 'toml'] = 'toml',  # noqa: A002
) -> None:
	"""Print the complete extension specification.

	Parameters:
		proj: Location specifier for `blext` projects.
		blext_info: Information used to find and load `blext` project.
		global_config: Loaded global configuration.
		format: The text format to show the Blender manifest as.
	"""
	blext_info = blext_info.parse_proj(proj)
	blext_spec = blext_info.blext_spec(global_config)

	bl_versions = blext_info.bl_versions(global_config)
	bl_platforms = blext_info.bl_platforms(global_config)
	if len(bl_versions) == 1:
		bl_version = next(iter(bl_versions))
		if len(bl_platforms) == 1:
			bl_platform = next(iter(bl_platforms))
			CONSOLE.print(
				blext_spec.bl_manifest_strs(
					bl_version.max_manifest_version,
					fmt=format,
				)[bl_version][bl_platform],
				markup=False,
				end='',
			)
		else:
			msgs = [
				'Please select only one `BLPlatform`, to show its `blender_manifest.toml`.',
				'> **Available Platforms**:',
				*[
					f'> - {granular_bl_platform}'
					for granular_bl_platform in blext_spec.granular_bl_platforms
				],
				'>',
				'> You can specify one (or more) using `--platform`.',
			]
			raise ValueError(*msgs)
	else:
		msgs = [
			'Please select only one `BLVersion`, to show its `blender_manifest.toml`.',
			'> **Available `BLVersion`s**:',
			*[
				f'> - {granular_bl_version.pretty_version}'
				for granular_bl_version in blext_spec.granular_bl_versions
			],
			'>',
			'> You can specify one (or more) using `--bl-version`.',
		]
		raise ValueError(*msgs)
