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

"""Tests `blext.pydeps.pydep`."""

import hypothesis as hyp
import packaging.utils
import packaging.version
from frozendict import frozendict
from hypothesis import strategies as st

from blext import pydeps
from blext.pydeps.pydep import RE_PYDEP_NAME, RE_PYDEP_VERSION

####################
# - Constants
####################
ST_PYDEP_NOWHEELS_NODEPS = st.builds(
	pydeps.PyDep,
	name=st.from_regex(RE_PYDEP_NAME),
	version_string=st.from_regex(RE_PYDEP_VERSION),
	registry=st.just('https://pypi.org/simple'),
	wheels=st.just(frozenset[pydeps.PyDepWheel]()),
	deps=st.just(frozendict[str, pydeps.PyDepMarker | None]()),
)

ST_PYDEP_NOWHEELS = st.builds(
	pydeps.PyDep,
	name=st.from_regex(RE_PYDEP_NAME),
	version_string=st.from_regex(RE_PYDEP_VERSION),
	registry=st.just('https://pypi.org/simple'),
	wheels=st.just(frozenset[pydeps.PyDepWheel]()),
	deps=st.dictionaries(
		keys=st.from_regex(RE_PYDEP_NAME),
		values=st.just(None),
	),
)

ST_PYDEP = st.builds(
	pydeps.PyDep,
	name=st.from_regex(RE_PYDEP_NAME),
	version_string=st.from_regex(RE_PYDEP_VERSION),
	registry=st.just('https://pypi.org/simple'),
	wheels=st.just(frozenset[pydeps.PyDepWheel]()),
	deps=st.just(frozendict[str, pydeps.PyDepMarker | None]()),
)


####################
# - Tests
####################
@hyp.given(ST_PYDEP_NOWHEELS_NODEPS)
def test_pydep_name_normalized(pydep: pydeps.PyDep) -> None:
	"""Test that `name` has been normalized."""
	assert packaging.utils.is_normalized_name(pydep.name)


@hyp.given(ST_PYDEP_NOWHEELS_NODEPS)
def test_pydep_version_string_normalized(pydep: pydeps.PyDep) -> None:
	"""Test that `version_string` has been normalized."""
	assert (
		packaging.utils.canonicalize_version(pydep.version_string)
		== pydep.version_string
	)


@hyp.given(ST_PYDEP_NOWHEELS_NODEPS)
def test_pydep_version_valid(pydep: pydeps.PyDep) -> None:
	"""Test that `version` is predictable and valid."""
	assert packaging.version.parse(pydep.version_string) == pydep.version


@hyp.given(ST_PYDEP_NOWHEELS)
def test_pydep_dep_names_normalized(pydep: pydeps.PyDep) -> None:
	"""Test that `name` has been normalized."""
	assert all(packaging.utils.is_normalized_name(dep_name) for dep_name in pydep.deps)


## TODO: Test Wheel Selection
## - Test that semivalid wheels have the expected compatibility.
## - Test that valid wheels have the expected compatibility.
## - Test that the "best wheel selection" is correct.
## - Don't worry about target_descendants or marker stuff. Test that higher up.
