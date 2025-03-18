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
# requires-python = "==3.11"
# dependencies = []
#
# [project]
# name = "minimal_script"
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
#     'linux-x64',
#     'macos-arm64',
#     'windows-x64',
# ]
# ///

import tomllib
from pathlib import Path

import bpy

####################
# - Constants
####################
PATH_MANIFEST = Path(__file__).resolve().parent / 'blender_manifest.toml'
with PATH_MANIFEST.open('rb') as f:
	ADDON_NAME: str = tomllib.load(f)['id']


####################
# - Operator: Hello World
####################
class HelloWorldOperator(bpy.types.Operator):
	"""Report "Hello, World!" when executed by the user."""

	bl_idname: str = f'{ADDON_NAME}.hello_world_operator'
	bl_label: str = 'Hello World Operator'

	@classmethod
	def poll(cls, _: bpy.types.Context) -> bool:
		"""Always allow the operator to run."""
		return True

	def execute(self, _: bpy.types.Context) -> set[str]:
		"""Report "Hello, World!"."""
		self.report({'INFO'}, 'Hello, World!')
		return {'FINISHED'}


####################
# - Menus
####################
def show_menu(menu: bpy.types.Menu, _: bpy.types.Context) -> None:
	menu.layout.operator(HelloWorldOperator.bl_idname, text=HelloWorldOperator.bl_label)


####################
# - Registration
####################
def register() -> None:
	bpy.utils.register_class(HelloWorldOperator)
	bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister() -> None:
	bpy.utils.unregister_class(HelloWorldOperator)
	bpy.types.VIEW3D_MT_object.remove(menu_func)
