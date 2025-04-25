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

"""Simple example of a Blender extension project that uses a few dependencies."""

import bpy
import numpy as np
import scipy as sc

ADDON_NAME = 'simple_proj'


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
			(
				f'sc.constants.speed_of_light={sc.constants.speed_of_light}'
				f'np.__version__={np.__version__}'
			),
		)

		return {'FINISHED'}


####################
# - Menus
####################
def show_menu(menu: bpy.types.Menu, _: bpy.types.Context) -> None:
	"""Draw `SimpleOperator` within a menu."""
	menu.layout.operator(SimpleOperator.bl_idname, text=SimpleOperator.bl_label)


####################
# - Registration
####################
def register() -> None:
	"""Register this extension."""
	bpy.utils.register_class(SimpleOperator)
	bpy.types.VIEW3D_MT_object.append(show_menu)


def unregister() -> None:
	"""Unregister this extension."""
	bpy.utils.unregister_class(SimpleOperator)
	bpy.types.VIEW3D_MT_object.remove(show_menu)
