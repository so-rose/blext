import bpy

from .. import contracts as ct

bpy.types.Scene.simple_integer = bpy.props.IntProperty(
	name='Simple Integer',
	description="It's just an integer! What's the big deal?",
	default=10,
)


class SimplePanel(bpy.types.Panel):
	bl_idname = ct.PanelType.SimplePanel
	bl_label = 'Simple Panel'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = 'scene'

	@classmethod
	def poll(cls, _: bpy.types.Context) -> bool:
		"""Always show panel in Scene properties.

		Notes:
			Run by Blender when trying to show a panel.

		Returns:
			Whether the panel can show.
		"""
		return True

	def draw(self, _: bpy.types.Context) -> None:
		"""Draw the panel w/options.

		Notes:
			Run by Blender when the panel needs to be displayed.

		Parameters:
			context: The Blender context object.
				Must contain `context.window_manager` and `context.workspace`.
		"""
		layout = self.layout

		# Operator
		layout.operator(ct.OperatorType.SimpleOperator)


####################
# - Blender Registration
####################
BL_REGISTER = [SimplePanel]
BL_HANDLERS: ct.BLHandlers = ct.BLHandlers()
BL_KEYMAP_ITEMS: list[ct.BLKeymapItem] = []
