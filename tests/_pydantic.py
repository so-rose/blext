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

import hypothesis.provisional as st_provisional
import pydantic as pyd
from hypothesis import strategies as st

import blext


####################
# - pydantic Helpers
####################
def fix_pattern(pattern: str) -> str:
	# pydantic and hypothesis don't agree how to apply regexes
	if pattern.endswith('$'):
		return pattern[0:-1] + r'\Z'
	return pattern


def get_pattern(model: type[pyd.BaseModel], field: str) -> str:
	for data in model.model_fields[field].metadata:
		if hasattr(data, 'pattern'):
			return fix_pattern(data.pattern)
	raise ValueError(f'pattern not found in {model.__name__}.{field}')


st.register_type_strategy(pyd.HttpUrl, st_provisional.urls())
st.register_type_strategy(pyd.ByteSize, st.integers(min_value=0))

ST_BLEXT_SPEC = st.builds(
	blext.BLExtSpec,
	tagline=st.from_regex(get_pattern(blext.BLExtSpec, 'tagline')),
	blender_version_min=st.from_regex(
		get_pattern(blext.BLExtSpec, 'blender_version_min')
	),
	blender_version_max=st.from_regex(
		get_pattern(blext.BLExtSpec, 'blender_version_max')
	),
)
