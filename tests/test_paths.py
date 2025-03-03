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
from blext import paths

from ._context import EXAMPLES_PROJ_FILES_VALID


@hyp.given(
	st.sampled_from(EXAMPLES_PROJ_FILES_VALID),
	st.sampled_from(typ.get_args(blext.StandardReleaseProfile)),
)
def test_paths(
	proj_uri: Path,
	release_profile_id: blext.StandardReleaseProfile,
) -> None:
	blext_spec = blext.blext_info.load_blext_spec(
		proj_uri, release_profile_id=release_profile_id
	)
	_ = paths.path_root(blext_spec)
	_ = paths.path_dev(blext_spec)
	_ = paths.path_wheels(blext_spec)
	_ = paths.path_prepack(blext_spec)
	_ = paths.path_build(blext_spec)
	_ = paths.path_local(blext_spec)
