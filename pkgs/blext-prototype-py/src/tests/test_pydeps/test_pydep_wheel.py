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

"""Tests `blext.pydeps.pydep_wheel`."""

from hypothesis import provisional as st_prov
from hypothesis import strategies as st

from blext import pydeps
from blext.pydeps.pydep_wheel import RE_SHA256_HASH

####################
# - Constants
####################
ST_PYDEP_WHEEL = st.builds(
	pydeps.PyDep,
	url=st_prov.urls(),
	registry=st.just('https://pypi.org/simple'),
	hash=st.from_regex(RE_SHA256_HASH),
	size=st.integers(),
)
