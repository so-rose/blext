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

"""Tests `blext.extyp.bl_platform_set`."""

import functools

import hypothesis as hyp
from hypothesis import strategies as st

from blext import extyp, pydeps
from blext.extyp.bl_platform_set import IPyDepWheel

ST_BL_PLATFORMS = st.frozensets(
	st.sampled_from(extyp.BLPlatform),
	min_size=1,
)


####################
# - Tests: Type Stubs
####################
def test_pydep_wheel_stub_is_compatible() -> None:
	"""Test that the type stub `IPyDepWheel` is actually representative of `pydeps.PyDepWheel`."""
	assert issubclass(pydeps.PyDepWheel, IPyDepWheel)


####################
# - Tests: Creation
####################
@hyp.given(st.sampled_from(extyp.BLPlatform))
def test_create_from_single_bl_platform(bl_platform: extyp.BLPlatform) -> None:
	"""Test that `BLPlatformSet` can be created from several `BLPlatform`s."""
	bl_platform_set = extyp.BLPlatformSet.from_bl_platform(bl_platform)

	assert str(bl_platform) == str(bl_platform_set)


@hyp.given(ST_BL_PLATFORMS)
def test_create_from_bl_platforms(bl_platforms: frozenset[extyp.BLPlatform]) -> None:
	"""Test that `BLPlatformSet` can be created from several `BLPlatform`s."""
	bl_platform_set = extyp.BLPlatformSet.from_bl_platforms(bl_platforms)

	assert str(bl_platform_set) == '_'.join(sorted(bl_platforms))


####################
# - Tests: BLPlatform Access
####################
@hyp.given(ST_BL_PLATFORMS)
def test_sorted_bl_platforms(bl_platforms: frozenset[extyp.BLPlatform]) -> None:
	"""Test that `BLPlatformSet.sorted_bl_platforms` contains the sorted order of the tuple passed to the creation method."""
	bl_platforms_tuple = tuple(bl_platforms)

	bl_platform_set = extyp.BLPlatformSet.from_bl_platforms(bl_platforms_tuple)

	assert bl_platform_set.sorted_bl_platforms == tuple(sorted(bl_platforms_tuple))


@hyp.given(ST_BL_PLATFORMS)
def test_bl_platforms(bl_platforms: frozenset[extyp.BLPlatform]) -> None:
	"""Test that `BLPlatformSet.sorted_bl_platforms` preserves the order passed to the creation method."""
	bl_platform_set = extyp.BLPlatformSet.from_bl_platforms(bl_platforms)

	assert bl_platform_set.bl_platforms == bl_platforms


####################
# - Tests: Archive Information
####################
@hyp.given(ST_BL_PLATFORMS)
def test_official_archive_file_exts(bl_platforms: frozenset[extyp.BLPlatform]) -> None:
	"""Whether official archive file extension matches the hard-coded truth."""
	bl_platform_set = extyp.BLPlatformSet.from_bl_platforms(bl_platforms)

	assert bl_platform_set.official_archive_file_exts == frozenset({
		bl_platform.wheel_platform_tag_prefix
		for bl_platform in bl_platform_set.bl_platforms
	})


####################
# - Tests: PyPi Information
####################
@hyp.given(ST_BL_PLATFORMS)
def test_pypi_arches(bl_platforms: frozenset[extyp.BLPlatform]) -> None:
	"""Whether each platform's supported PyPi architectures precisely matches a hard-coded mapping."""
	bl_platform_set = extyp.BLPlatformSet.from_bl_platforms(bl_platforms)

	assert bl_platform_set.pypi_arches == functools.reduce(
		lambda a, b: a | b,
		(bl_platform.pypi_arches for bl_platform in bl_platform_set.bl_platforms),
	)


@hyp.given(ST_BL_PLATFORMS)
def test_wheel_platform_tag_prefixes(bl_platforms: frozenset[extyp.BLPlatform]) -> None:
	"""Whether each platform's supported PyPi architectures precisely matches a hard-coded mapping."""
	bl_platform_set = extyp.BLPlatformSet.from_bl_platforms(bl_platforms)

	assert bl_platform_set.wheel_platform_tag_prefixes == frozenset({
		bl_platform.wheel_platform_tag_prefix
		for bl_platform in bl_platform_set.bl_platforms
	})


####################
# - Tests: Pymarker Information
####################
@hyp.given(ST_BL_PLATFORMS)
def test_pymarker_os_names(bl_platforms: frozenset[extyp.BLPlatform]) -> None:
	"""Whether each `os.name` matches the expected value."""
	bl_platform_set = extyp.BLPlatformSet.from_bl_platforms(bl_platforms)

	assert bl_platform_set.pymarker_os_names == frozenset({
		bl_platform.pymarker_os_name for bl_platform in bl_platform_set.bl_platforms
	})


@hyp.given(ST_BL_PLATFORMS)
def test_pymarker_platform_machines(bl_platforms: frozenset[extyp.BLPlatform]) -> None:
	"""Whether each `platform.machine()` matches the expected value."""
	bl_platform_set = extyp.BLPlatformSet.from_bl_platforms(bl_platforms)

	assert bl_platform_set.pymarker_platform_machines == functools.reduce(
		lambda a, b: a | b,
		(
			bl_platform.pymarker_platform_machines
			for bl_platform in bl_platform_set.bl_platforms
		),
	)


@hyp.given(ST_BL_PLATFORMS)
def test_pymarker_platform_systems(bl_platforms: frozenset[extyp.BLPlatform]) -> None:
	"""Whether each `platform.system()` matches the expected value."""
	bl_platform_set = extyp.BLPlatformSet.from_bl_platforms(bl_platforms)

	assert bl_platform_set.pymarker_platform_systems == frozenset({
		bl_platform.pymarker_platform_system
		for bl_platform in bl_platform_set.bl_platforms
	})


@hyp.given(ST_BL_PLATFORMS)
def test_pymarker_sys_platform(bl_platforms: frozenset[extyp.BLPlatform]) -> None:
	"""Whether each `sys.platform` matches the expected value."""
	bl_platform_set = extyp.BLPlatformSet.from_bl_platforms(bl_platforms)

	assert bl_platform_set.pymarker_sys_platforms == frozenset({
		bl_platform.pymarker_sys_platform
		for bl_platform in bl_platform_set.bl_platforms
	})


## TODO: Test smooshing.
