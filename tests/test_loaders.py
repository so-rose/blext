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

import typing as typ
from pathlib import Path

import hypothesis as hyp
from hypothesis import strategies as st

import blext
from blext import blext_info

from ._context import EXAMPLES_PROJ_FILES_VALID


####################
# - Tests: Parse Examples
####################
@hyp.given(
	st.sampled_from(EXAMPLES_PROJ_FILES_VALID),
	st.sampled_from(typ.get_args(blext.StandardReleaseProfile)),
)
def test_load_path_uri(
	proj_uri: Path,
	release_profile_id: blext.StandardReleaseProfile,
) -> None:
	_ = blext_info.load_blext_spec(proj_uri, release_profile_id=release_profile_id)


@hyp.given(
	st.sampled_from(EXAMPLES_PROJ_FILES_VALID),
	st.sampled_from(typ.get_args(blext.StandardReleaseProfile)),
)
def test_load_path_registration(
	proj_uri: Path,
	release_profile_id: blext.StandardReleaseProfile,
) -> None:
	blext_spec = blext_info.load_blext_spec(
		proj_uri, release_profile_id=release_profile_id
	)
	assert (
		blext.paths.path_root(blext_spec) == proj_uri
		or proj_uri.is_relative_to(blext.paths.path_root(blext_spec))
		or blext.paths.path_root(blext_spec).is_relative_to(
			blext.paths.CONFIG.path_global_script_cache
		)
	)


@hyp.given(
	st.sampled_from(EXAMPLES_PROJ_FILES_VALID),
	st.sampled_from(typ.get_args(blext.StandardReleaseProfile)),
	st.sampled_from(
		[
			blext.BLPlatform.linux_x64,
			blext.BLPlatform.macos_arm64,
			blext.BLPlatform.windows_x64,
		]
	),
)
def test_load_spec_and_inject_bl_platform(
	proj_uri: Path,
	release_profile_id: blext.StandardReleaseProfile,
	bl_platform: blext.BLPlatform,
) -> None:
	blext_spec = blext_info.load_bl_platform_into_spec(
		blext_info.load_blext_spec(proj_uri, release_profile_id=release_profile_id),
		bl_platform_ref=bl_platform,
	)
	assert next(iter(blext_spec.bl_platforms)) == bl_platform
