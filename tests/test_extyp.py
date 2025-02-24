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

import hypothesis as hyp
from hypothesis import strategies as st

from blext import extyp


####################
# - Constant / Helpers
####################
####################
# - Tests
####################
@hyp.given(
	st.sampled_from(
		[
			'linux-x64',
			'linux-arm64',
			'macos-x64',
			'macos-arm64',
			'windows-x64',
			'windows-arm64',
		]
	)
)
def test_create_bl_platform(bl_platform_str: str):
	extyp.BLPlatform(bl_platform_str)
