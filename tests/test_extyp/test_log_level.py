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

"""Tests `blext.extyp.log_level`."""

import hypothesis as hyp
from hypothesis import strategies as st

from blext import extyp


####################
# - Tests: Parse Examples
####################
@hyp.given(
	st.sampled_from(extyp.BLExtLogLevel),
)
def test_int_log_level_is_valid(blext_log_level: extyp.BLExtLogLevel) -> None:
	"""Whether the `.log_level` property produces an integer that is usable for logging, aka. a positive integer."""
	assert isinstance(blext_log_level.log_level, int)
	assert blext_log_level.log_level > 0
