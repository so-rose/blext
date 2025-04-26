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

"""Abstractions relevant for Blender extensions."""

from . import validators
from .bl_manifest import BLManifest, BLManifest1_0_0
from .bl_manifest_version import BLManifestVersion
from .bl_platform import BLPlatform
from .bl_platform_set import BLPlatformSet
from .bl_release import BLRelease
from .bl_release_detected import BLReleaseDetected
from .bl_release_official import BLReleaseOfficial
from .bl_version import BLVersion
from .blext_location import BLExtLocation
from .blext_location_git import BLExtLocationGit
from .blext_location_http import BLExtLocationHttp
from .blext_location_path import BLExtLocationPath
from .log_level import BLExtLogLevel
from .release_profile import ReleaseProfile, StandardReleaseProfile
from .spdx_license import SPDXLicense

__all__ = [
	'BLExtLocation',
	'BLExtLocationGit',
	'BLExtLocationHttp',
	'BLExtLocationPath',
	'BLExtLogLevel',
	'BLManifest',
	'BLManifest1_0_0',
	'BLManifestVersion',
	'BLPlatform',
	'BLPlatformSet',
	'BLRelease',
	'BLReleaseDetected',
	'BLReleaseOfficial',
	'BLVersion',
	'ReleaseProfile',
	'SPDXLicense',
	'StandardReleaseProfile',
	'validators',
]
