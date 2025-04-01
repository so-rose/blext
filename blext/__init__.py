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

"""`blext` is a project manager for Blender extension development."""

from . import blender, pack, pydeps
from .extyp import (
	BLExtLogLevel,
	BLManifest,
	BLManifest_1_0_0,
	BLManifestVersion,
	BLPlatform,
	BLReleaseDiscovered,
	BLReleaseOfficial,
	BLVersion,
	BLVersionSource,
	BLVersionSourceGit,
	BLVersionSourceOfficial,
	BLVersionSources,
	ReleaseProfile,
	SPDXLicense,
	StandardReleaseProfile,
)
from .spec import BLExtSpec

__all__ = [
	'BLExtLogLevel',
	'BLExtSpec',
	'BLManifest',
	'BLManifestVersion',
	'BLManifest_1_0_0',
	'BLPlatform',
	'BLReleaseDiscovered',
	'BLReleaseOfficial',
	'BLVersion',
	'BLVersionSource',
	'BLVersionSourceGit',
	'BLVersionSourceOfficial',
	'BLVersionSources',
	'BLVersionSources',
	'ReleaseProfile',
	'SPDXLicense',
	'StandardReleaseProfile',
	'blender',
	'pack',
	'pydeps',
]
