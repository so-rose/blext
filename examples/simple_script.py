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
# requires-python = "==3.11.*"
# dependencies = [
#     "jupyter-core>=5.7.2",
#     "polars[async]>=1.26.0",
#     "scipy>=1.15.2",
#     "autopep8==2.3.1", # # ⭳⭳⭳ MANAGED BY BLEXT ⭳⭳⭳
#     "certifi==2021.10.8",
#     "charset_normalizer==2.0.10",
#     "cython==0.29.30",
#     "idna==3.3",
#     "numpy==1.24.3",
#     "pip==24.0",
#     "pycodestyle==2.12.1",
#     "requests==2.27.1",
#     "setuptools==63.2.0",
#     "urllib3==1.26.8",
#     "zstandard==0.16.0", # # ⭱⭱⭱ MANAGED BY BLEXT ⭱⭱⭱
# ]
#
# [project]
# name = "simple_script"
# version = "0.1.0"
# description = "A quick example of a one-file Blender w/Python dependencies"
# authors = [
#     { name = "John Doe", email = "jdoe@example.com" },
# ]
# license = "AGPL-3.0-or-later"
#
# [tool.blext]
# pretty_name = "Single File Extension Example"
# blender_version_min = '4.3.0'
# blender_version_max = '4.4.0'
# bl_tags = ["Development"]
# copyright = ["2025 blext Contributors"]
#
# supported_platforms = [
#    'windows-x64',
#    'macos-arm64',
#    'linux-x64',
# ]
# min_macos_version = [12, 0]
# ///

"""Simple example of a Blender extension that uses a few dependencies."""

import bpy
import numpy as np
import scipy as sc

ADDON_NAME = 'simple_script'


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
