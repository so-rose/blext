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

"""Implements `BLVersionSource`."""

import functools

import pydantic as pyd


####################
# - Blender Version Source
####################
class BLVersionSource(pyd.BaseModel, frozen=True):
	"""A locatable version of Blender."""

	####################
	# - Overrides
	####################
	@functools.cached_property
	def version(self) -> str:
		"""Some kind of unique identifier of the referenced Blender version."""
		raise NotImplementedError

	@functools.cached_property
	def blender_version_min(self) -> str:
		"""Minimum supported Blender version.

		Warnings:
			**Do not parse**. Only for specialized use.

			**Do not use `self.version`** either.

			Instead, handle versions in a manner consistent with each particular `BLVersionSource` subclass.

		Notes:
			- Must correspond to an official releases `>=4.2.0`.
			- Corresponds directly to the same-named property in `blender_manifest.toml`.
			- The `blender_manifest.toml` format enforces that this be given by all `BLVersion`s. For ex. forks that don't always have such a clean descriptor, it's okay to lie to make it work.
		"""
		raise NotImplementedError

	@functools.cached_property
	def blender_version_max(self) -> str | None:
		"""Maximum supported Blender version, **not including** this version.

		Warnings:
			**Do not parse**. Only for specialized use.

			**Do not use `self.version`** either.

			Instead, handle versions in a manner consistent with each particular `BLVersionSource` subclass.

		Notes:
			- Must correspond to an official release `>=4.2.1`.
			- Corresponds directly to the same-named property in `blender_manifest.toml`.
			- Does not have to be given.
		"""
		return None
