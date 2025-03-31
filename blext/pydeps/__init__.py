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

"""Manage Python dependencies of Blender extensions."""

from . import uv
from .blext_deps import BLExtDeps
from .download import download_wheel, download_wheels
from .pydep import PyDep
from .pydep_marker import PyDepMarker
from .pydep_wheel import MANYLINUX_LEGACY_ALIASES, PyDepWheel

__all__ = [
	'MANYLINUX_LEGACY_ALIASES',
	'BLExtDeps',
	'PyDep',
	'PyDepMarker',
	'PyDepWheel',
	'download_wheel',
	'download_wheels',
	'pydep',
	'uv',
]
