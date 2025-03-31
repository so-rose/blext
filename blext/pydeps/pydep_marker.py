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

import functools

import packaging.markers
import pydantic as pyd

from blext import extyp


class PyDepMarker(pyd.BaseModel, frozen=True):
	"""A platform-specific criteria for installing a particular wheel."""

	marker_str: str
	## TODO: Validate against formal grammer?

	####################
	# - Properties
	####################
	@functools.cached_property
	def marker(self) -> packaging.markers.Marker:
		"""Parsed marker whose `evaluate()` method checks it against a Python environment."""
		return packaging.markers.Marker(self.marker_str)

	####################
	# - Methods
	####################
	def is_valid_for(
		self,
		*,
		pkg_name: str,
		bl_version: extyp.BLVersion,
		bl_platform: extyp.BLPlatform,
	) -> bool:
		"""Whether this marker will evaluate `True` under the targeted Python environment.

		Notes:
			`pkg_name` is included, since the way that `uv` encodes conflicts between `extra`s is to add the package name, like so:
			- `extra-11-simple-proj-bl-4-3`
			- `extra-11-simple-proj-bl-4-4`
			- `extra-{len(pkg_name)}-{pkg_name}-{pymarker_extra}`

			Presumably, this prevents name-conflicts.

		Parameters:
			pkg_name: The name of the root package, defined with standard `_`.
				- Used for the package-encoded version of the extras.
			bl_version: The Blender version to check validity for.
			bl_platform: The Blender platform to check validity for.

		See Also:
			`extyp.BLVersion.pymarker_encoded_package_extra`: For more information about how and why `uv`-generated `extra`s require `pkg_name` to be known.

		"""
		return any(
			self.marker.evaluate(environment=pymarker_environment)
			for pymarker_environment in [
				# dict() each 'environment' by-platform.
				## - 'pymarker_environment' encodes the 'extra' corresponding to the Blender version.
				## - For example: {'extra': 'bl4-2'}
				## - By specifying 'pkg_name', 'pymarker_environment' also has 'extra' by-package.
				## - For example: {'extra': 'extra-11-simple-proj-bl4-2'}
				dict(pymarker_environment)
				for pymarker_environment in bl_version.pymarker_environments(
					pkg_name=pkg_name
				)[bl_platform]
			]
		)
