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

"""Implements `BLReleaseDiscovered`."""

import typing as typ

from .bl_version import BLVersion


class BLRelease(typ.Protocol):
	"""Particular known release of Blender."""

	@property
	def bl_version(self) -> BLVersion:
		"""The Blender version corresponding to this release."""
		raise NotImplementedError
