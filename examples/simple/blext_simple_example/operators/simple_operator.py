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
