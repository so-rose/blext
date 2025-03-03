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

import tempfile
import typing as typ
from pathlib import Path

import hypothesis as hyp
from hypothesis import strategies as st

import blext
from blext import pack

from ._context import EXAMPLES_PROJ_FILES_VALID


####################
# - Tests: Parse Examples
####################
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
def test_pack_example_extension(
	proj_file_path: Path,
	release_profile_id: blext.StandardReleaseProfile,
	bl_platform: blext.BLPlatform,
) -> None:
	blext_spec = blext.BLExtSpec.from_proj_spec_path(
		proj_file_path,
		release_profile_id=release_profile_id,
	)
	blext_spec = blext_spec.set_bl_platforms(bl_platform)
	with tempfile.TemporaryDirectory() as path_tmpdir_str:
		path_tmpdir = Path(path_tmpdir_str)

		path_zip = path_tmpdir / blext_spec.packed_zip_filename
		path_zip_prepack = path_tmpdir / ('prepack_' + blext_spec.packed_zip_filename)

		if proj_file_path.name.endswith('.py'):
			path_pypkg = None
			path_pysrc = proj_file_path
			path_uv_lock = proj_file_path.parent / (proj_file_path.name + '.lock')
		else:
			path_pypkg = proj_file_path
			path_pysrc = None
			path_uv_lock = proj_file_path.parent / 'uv.lock'

		pack.pack_bl_extension(
			blext_spec,
			vendor=False,
			force_prepack=True,
			path_zip=path_zip,
			path_zip_prepack=path_zip_prepack,
			path_uv_lock=path_uv_lock,
			path_pypkg=path_pypkg,
			path_pysrc=path_pysrc,
		)
