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

"""Shared context for tests."""

import collections.abc as cabc
import itertools
import typing as typ
from pathlib import Path

import hypothesis.provisional as st_provisional
import pydantic as pyd
from hypothesis import strategies as st
from pydantic_extra_types.semantic_version import SemanticVersion

####################
# - Constants
####################
PATH_ROOT = Path(__file__).resolve().parent.parent

SEMVER_REGEX = r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'

EXAMPLES_PROJ_FILES_VALID = [
	PATH_ROOT / 'examples' / 'simple' / 'pyproject.toml',
	PATH_ROOT / 'examples' / 'minimal_file_ext.py',
]

EXAMPLES_PROJ_FILES_INVALID = [
	PATH_ROOT,
	PATH_ROOT / 'examples' / 'simple',
	PATH_ROOT / 'examples' / 'simpl',
	PATH_ROOT / 'examples' / 'simple' / 'pyproject.json',
	PATH_ROOT / 'examples' / 'simple' / 'uv.lock',
	PATH_ROOT / 'minimal_file_ext.py.lock',
]


####################
# - Helpers
####################
T = typ.TypeVar('T')


def powerset(iterable: cabc.Iterable[T]) -> itertools.chain[tuple[T, ...]]:
	"""Computes the power set of the input iterable lazily."""
	s = tuple(iterable)
	return itertools.chain.from_iterable(
		itertools.combinations(s, r) for r in range(len(s) + 1)
	)


####################
# - pydantic Helpers
####################
##def fix_pattern(pattern: str) -> str:
##	# pydantic and hypothesis don't agree how to apply regexes
##	if pattern.endswith('$'):
##		return pattern[0:-1] + r'\Z'
##	return pattern
##
##
##def get_pattern(model: type[pyd.BaseModel], field: str) -> str:
##	for data in model.model_fields[field].metadata:
##		if hasattr(data, 'pattern'):
##			return fix_pattern(data.pattern)
##	raise ValueError(f'pattern not found in {model.__name__}.{field}')


st.register_type_strategy(pyd.HttpUrl, st_provisional.urls())
st.register_type_strategy(pyd.ByteSize, st.integers(min_value=0))
st.register_type_strategy(
	SemanticVersion,
	strategy=st.from_regex(
		r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)?$'
	),
)
