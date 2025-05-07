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

"""Tests `blext.extyp.bl_platform`."""

import hypothesis as hyp
import pytest
from hypothesis import strategies as st

from blext import extyp

####################
# - Constants
####################
PYPI_ARCHES = {
	extyp.BLPlatform.linux_x64: frozenset({'x86_64'}),
	extyp.BLPlatform.linux_arm64: frozenset({'aarch64', 'armv7l', 'arm64'}),
	extyp.BLPlatform.macos_x64: frozenset({
		'x86_64',
		'universal',
		'universal2',
		'intel',
		'fat3',
		'fat64',
	}),
	extyp.BLPlatform.macos_arm64: frozenset({'arm64', 'universal2'}),
	extyp.BLPlatform.windows_x64: frozenset({'amd64'}),
	extyp.BLPlatform.windows_arm64: frozenset({'arm64'}),
}

PYMARKER_PLATFORM_MACHINES = {
	extyp.BLPlatform.linux_x64: frozenset({'x86_64'}),
	extyp.BLPlatform.linux_arm64: frozenset({'aarch64', 'armv7l', 'arm64'}),
	extyp.BLPlatform.macos_x64: frozenset({'x86_64', 'i386'}),
	extyp.BLPlatform.macos_arm64: frozenset({'arm64'}),
	extyp.BLPlatform.windows_x64: frozenset({'amd64'}),
	extyp.BLPlatform.windows_arm64: frozenset({'arm64'}),
}


####################
# - Tests: Platform Checks
####################
@hyp.given(st.sampled_from(extyp.BLPlatform))
def test_is_windows(bl_platform: extyp.BLPlatform) -> None:
	"""Windows platform check should succeed when the enum starts with `windows`."""
	assert bl_platform.is_windows == bl_platform.startswith('windows')


####################
# - Tests: Archive Information
####################
@hyp.given(st.sampled_from(extyp.BLPlatform))
def test_official_archive_file_ext(bl_platform: extyp.BLPlatform) -> None:
	"""Whether official archive file extension matches the hard-coded truth."""
	if bl_platform.startswith('linux'):
		assert bl_platform.official_archive_file_ext == 'tar.xz'
	elif bl_platform.startswith('macos'):
		assert bl_platform.official_archive_file_ext == 'dmg'
	elif bl_platform.startswith('windows'):
		assert bl_platform.official_archive_file_ext == 'zip'
	else:
		pytest.fail("`bl_platform` didn't start with `linux`, `macos`, or `windows`")


####################
# - Tests: PyPi Information
####################
@hyp.given(st.sampled_from(extyp.BLPlatform))
def test_pypi_arches(bl_platform: extyp.BLPlatform) -> None:
	"""Whether each platform's supported PyPi architectures precisely matches a hard-coded mapping."""
	assert bl_platform.pypi_arches == PYPI_ARCHES[bl_platform]


@hyp.given(st.sampled_from(extyp.BLPlatform))
def test_wheel_platform_tag_prefix(bl_platform: extyp.BLPlatform) -> None:
	"""Whether each platform's supported PyPi architectures precisely matches a hard-coded mapping."""
	if bl_platform.startswith('linux'):
		assert bl_platform.wheel_platform_tag_prefix == 'manylinux_'
	elif bl_platform.startswith('macos'):
		assert bl_platform.wheel_platform_tag_prefix == 'macosx_'
	elif bl_platform.startswith('windows'):
		assert bl_platform.wheel_platform_tag_prefix == 'win'
	else:
		pytest.fail("`bl_platform` didn't start with `linux`, `macos`, or `windows`")


####################
# - Tests: Pymarker Information
####################
@hyp.given(st.sampled_from(extyp.BLPlatform))
def test_pymarker_os_name(bl_platform: extyp.BLPlatform) -> None:
	"""Whether each `os.name` matches the expected value."""
	if bl_platform.startswith(('linux', 'macos')):
		assert bl_platform.pymarker_os_name == 'posix'
	elif bl_platform.startswith('windows'):
		assert bl_platform.pymarker_os_name == 'nt'
	else:
		pytest.fail("`bl_platform` didn't start with `linux`, `macos`, or `windows`")


@hyp.given(st.sampled_from(extyp.BLPlatform))
def test_pymarker_platform_machines(bl_platform: extyp.BLPlatform) -> None:
	"""Whether each `platform.machine()` matches the expected value."""
	assert (
		bl_platform.pymarker_platform_machines
		== PYMARKER_PLATFORM_MACHINES[bl_platform]
	)


@hyp.given(st.sampled_from(extyp.BLPlatform))
def test_pymarker_platform_system(bl_platform: extyp.BLPlatform) -> None:
	"""Whether each `platform.system()` matches the expected value."""
	if bl_platform.startswith('linux'):
		assert bl_platform.pymarker_platform_system == 'Linux'
	elif bl_platform.startswith('macos'):
		assert bl_platform.pymarker_platform_system == 'Darwin'
	elif bl_platform.startswith('windows'):
		assert bl_platform.pymarker_platform_system == 'Windows'
	else:
		pytest.fail("`bl_platform` didn't start with `linux`, `macos`, or `windows`")


@hyp.given(st.sampled_from(extyp.BLPlatform))
def test_pymarker_sys_platform(bl_platform: extyp.BLPlatform) -> None:
	"""Whether each `sys.platform` matches the expected value."""
	if bl_platform.startswith('linux'):
		assert bl_platform.pymarker_sys_platform == 'linux'
	elif bl_platform.startswith('macos'):
		assert bl_platform.pymarker_sys_platform == 'darwin'
	elif bl_platform.startswith('windows'):
		assert bl_platform.pymarker_sys_platform == 'win32'
	else:
		pytest.fail("`bl_platform` didn't start with `linux`, `macos`, or `windows`")
