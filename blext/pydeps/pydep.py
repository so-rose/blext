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

"""Implements `PyDep` and `PyDepMarker."""

import pydantic as pyd

from blext import extyp
from blext.utils.pydantic_frozendict import FrozenDict

from .pydep_marker import PyDepMarker
from .pydep_wheel import PyDepWheel


####################
# - Python Dependency
####################
class PyDep(pyd.BaseModel, frozen=True):
	"""A Python dependency."""

	name: str
	version: str
	registry: str
	wheels: frozenset[PyDepWheel]

	pydep_markers: FrozenDict[str, PyDepMarker | None]

	def select_wheel(
		self,
		*,
		bl_platform: extyp.BLPlatform,
		min_glibc_version: tuple[int, int],
		min_macos_version: tuple[int, int],
		valid_python_tags: frozenset[str],
		valid_abi_tags: frozenset[str],
		err_msgs: list[str],
	) -> PyDepWheel | None:
		"""Select the best wheel to satisfy this dependency."""
		####################
		# - Step 0: Find All Valid Wheels
		####################
		## - Any wheel in this list should work just fine.
		semivalid_wheels = [
			wheel
			for wheel in self.wheels
			# The wheel must work in an environment that supports the given python tags.
			if wheel.works_with_python_tags(valid_python_tags)
			# The wheel must work in an environment that supports the given ABI tags.
			and wheel.works_with_abi_tags(valid_abi_tags)
			and wheel.works_with_platform(
				bl_platform=bl_platform,
				min_glibc_version=None,
				min_macos_version=None,
			)
		]
		valid_wheels = [
			wheel
			for wheel in semivalid_wheels
			# The wheel must work in an environment provided by a given Blender platform.
			if wheel.works_with_platform(
				bl_platform=bl_platform,
				min_glibc_version=min_glibc_version,
				min_macos_version=min_macos_version,
			)
		]

		####################
		# - Step 1: Select "Best" Wheel
		####################
		## - Prefer some wheels over others in a platform-specific manner.
		## - For instance, one might want to prefer higher `glibc` versions when available.
		match bl_platform:
			case extyp.BLPlatform.linux_x64 | extyp.BLPlatform.linux_arm64:
				if valid_wheels:
					return sorted(
						valid_wheels,
						key=lambda wheel: wheel.sort_key_preferred_linux,
					)[0]

				osver_str = 'glibc'
				min_osver_str = '.'.join(str(i) for i in min_glibc_version)
				semivalid_wheel_osver_strs = {
					semivalid_wheel: ', '.join(
						'.'.join(str(i) for i in glibc_version)
						for glibc_version in semivalid_wheel.glibc_versions.values()
						if glibc_version is not None
					)
					for semivalid_wheel in semivalid_wheels
				}

			case extyp.BLPlatform.macos_x64 | extyp.BLPlatform.macos_arm64:
				if valid_wheels:
					return sorted(
						valid_wheels,
						key=lambda wheel: wheel.sort_key_preferred_mac,
					)[0]

				osver_str = 'macos'
				min_osver_str = '.'.join(str(i) for i in min_macos_version)
				semivalid_wheel_osver_strs = {
					semivalid_wheel: ', '.join(
						'.'.join(str(i) for i in macos_version)
						for macos_version in semivalid_wheel.macos_versions.values()
						if macos_version is not None
					)
					for semivalid_wheel in semivalid_wheels
				}

			case extyp.BLPlatform.windows_x64 | extyp.BLPlatform.windows_arm64:
				if valid_wheels:
					return sorted(
						valid_wheels,
						key=lambda wheel: wheel.sort_key_preferred_windows,
					)[0]

				err_msgs.extend(
					[
						f'**{self.name}** not found for `{bl_platform}`.',
						'> **Remedies**:',
						f'> 1. **Remove** `{self.name}` from `project.dependencies`.',
						f'> 2. **Remove** `{bl_platform}` from `tool.blext.supported_platforms`.',
					]
				)

				return None

		err_msgs.extend(
			[
				f'**{self.name}** not found for `{bl_platform}`.',
				f'> **Extension Supports**: `{osver_str} >= {min_osver_str}`',
				'>',
				'> ----',
				'> **Rejected Wheels**:',
				*[
					f'> - {semivalid_wheel.filename}: `{osver_str} >= {semivalid_wheel_osver_strs[semivalid_wheel]}`'
					for semivalid_wheel in semivalid_wheels
				],
				'>',
				'> ----',
				'> **Remedies**:',
				f'> 1. **Raise** `{osver_str}` version in `tool.blext.min_{osver_str}_version`.',
				f'> 2. **Remove** `{self.name}` from `project.dependencies`.',
				f'> 3. **Remove** `{bl_platform}` from `tool.blext.supported_platforms`.',
				'',
			]
		)
		return None
