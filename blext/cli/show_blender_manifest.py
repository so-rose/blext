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
	if len(bl_versions) == 1:
		bl_version = next(iter(bl_versions))
		CONSOLE.print(
			blext_spec.export_blender_manifest(
				bl_version.max_manifest_version,
				bl_version=bl_version,
				fmt=format,
			),
			markup=False,
			end='',
		)
