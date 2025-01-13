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

"""Defines the `StartJupyterKernel` operator.

Inspired by <https://github.com/cheng-chi/blender_notebook/blob/master/blender_notebook/kernel.py>
"""

import bpy

from .. import contracts as ct


class SimpleOperator(bpy.types.Operator):
	"""Operator that shows a message."""

	bl_idname = ct.OperatorType.SimpleOperator
	bl_label = 'Other Operator'

	@classmethod
	def poll(cls, _: bpy.types.Context) -> bool:
		"""Always allow operator to run."""
		return True

	def execute(self, _: bpy.types.Context) -> set[ct.BLOperatorStatus]:
		"""Display a simple message on execution."""
		self.report({'INFO'}, 'SimpleOperator was executed from blext_simple_example.')

		return {'FINISHED'}


####################
# - Blender Registration
####################
BL_REGISTER = [SimpleOperator]
BL_HANDLERS: ct.BLHandlers = ct.BLHandlers()
BL_KEYMAP_ITEMS: list[ct.BLKeymapItem] = []
