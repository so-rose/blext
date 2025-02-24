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

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jax~=0.5.0",
# ]
#
# [project]
# name = "extension_file"
# version = "0.1.0"
# description = "A quick example of a one-file Blender w/Python dependencies"
# authors = [
#     { name = "John Doe", email = "jdoe@example.com" },
# ]
# license = { text = "AGPL-3.0-or-later" }
#
# [tool.blext]
# pretty_name = "Single File Extension Example"
# blender_version_min = '4.3.0'
# blender_version_max = '4.3.100'
# bl_tags = ["Development"]
# copyright = ["2025 blext Contributors"]
#
# supported_platforms = [
# 	'windows-x64',
# 	'macos-arm64',
# 	'linux-x64',
# ]
# min_glibc_version = [2, 20]
# min_macos_version = [12, 0]
# ///

import bpy
import jax.numpy as jnp
import scipy as sc

ADDON_NAME = 'extension_file'


####################
# - Simple Operator
####################
class SimpleOperator(bpy.types.Operator):
	"""Operator that shows a message."""

	bl_idname = f'{ADDON_NAME}.simple_operator'
	bl_label = 'Simple Operator'

	@classmethod
	def poll(cls, _: bpy.types.Context) -> bool:
		"""Always allow operator to run."""
		return True

	def execute(self, _: bpy.types.Context) -> set[str]:
		"""Display a simple message on execution."""
		self.report(
			{'INFO'},
			f'jnp.array([1, 2, 3])={jnp.array([1, 2, 3])} and sc.constants.speed_of_light={sc.constants.speed_of_light}',
		)

		return {'FINISHED'}


####################
# - Menus
####################
def menu_func(self, context):
	self.layout.operator(SimpleOperator.bl_idname, text=SimpleOperator.bl_label)


####################
# - Registration
####################
def register() -> None:
	bpy.utils.register_class(SimpleOperator)
	bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister() -> None:
	bpy.utils.unregister_class(SimpleOperator)
	bpy.types.VIEW3D_MT_object.remove(menu_func)
