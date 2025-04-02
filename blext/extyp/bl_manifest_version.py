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

"""Defines the Blender extension specification."""

import enum
import functools

from semver.version import Version

from .bl_manifest import BLManifest, BLManifest_1_0_0


####################
# - Manifest 1.0.0
####################
class BLManifestVersion(enum.StrEnum):
	"""Known Blender extension manifest schema versions."""

	V1_0_0 = '1.0.0'

	@functools.cached_property
	def manifest_type(self) -> type[BLManifest]:
		"""Class representing this Blender manifest schema."""
		M = BLManifestVersion
		return {
			M.V1_0_0: BLManifest_1_0_0,
		}[self]

	@functools.cached_property
	def semantic_version(self) -> Version:
		"""Class representing this Blender manifest schema."""
		return Version.parse(self)
