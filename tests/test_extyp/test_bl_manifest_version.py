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

"""Tests `blext.extyp.bl_manifest_version`."""

import hypothesis as hyp
from hypothesis import strategies as st
from semver.version import Version

from blext import extyp


####################
# - Tests
####################
@hyp.given(
	st.sampled_from(extyp.BLManifestVersion),
)
def test_manifest_type_is_BLManifest_type(  # noqa: N802
	bl_manifest_version: extyp.BLManifestVersion,
) -> None:
	"""Test that `.manifest_type` produces one of the `BLManifest`-implementing types."""
	assert any(
		bl_manifest_version.manifest_type is ManifestType
		for ManifestType in [extyp.BLManifest_1_0_0]
	)


@hyp.given(
	st.sampled_from(extyp.BLManifestVersion),
)
def test_manifest_version_is_semantic_version(
	bl_manifest_version: extyp.BLManifestVersion,
) -> None:
	"""Whether the `.log_level` property produces an integer that is usable for logging, aka. a positive integer."""
	assert Version.parse(bl_manifest_version)
