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

"""Extension types serving as meaningful abstractions for managing Blender extensions.

Attributes:
	ValidBLExtPerms: Hardcoded list of valid extension permissions.
		- `files`: Access to any filesystem operations.
		- `network`: Access to the internet.
		- `clipboard`: Permission to read and/or write the system clipboard.
		- `camera`: Permission to capture photos or videos from system sources.
		- `microphone`: Permission to capture audio from system sources.

	ValidBLTags: Hardcoded list of valid extension tags.
"""

import enum
import functools
import typing as typ


class BLPlatform(enum.StrEnum):
	"""Identifier for a particular kind of OS/Architecture supported by Blender.

	Notes:
		Values correspond perfectly to the platforms defined in the official Blender extension manifest specification.

		**However**, note that there are many nuances and conventions when it comes to cross-platform identification of architectures.
		When interacting with other systems, ensure this is taken into account.

	Corresponds perfectly to the platforms defined in the Blender Extension Manifest.

	See Also:
		- `blext.finders`: Tools for detecting `BLPlatform`s.
	"""

	linux_x64 = 'linux-x64'
	linux_arm64 = 'linux-arm64'
	macos_x64 = 'macos-x64'
	macos_arm64 = 'macos-arm64'
	windows_x64 = 'windows-x64'
	windows_arm64 = 'windows-arm64'

	@functools.cached_property
	def is_windows(self) -> bool:
		"""Whether this is a Windows-based platform."""
		P = BLPlatform
		return self is P.windows_x64 or self is P.windows_arm64

	####################
	# - PyPi Information
	####################
	@functools.cached_property
	def official_archive_file_ext(self) -> str:
		"""File extension of Blender distributed officially and portably for this platform."""
		BLP = BLPlatform
		return {
			BLP.linux_x64: 'tar.xz',
			BLP.linux_arm64: 'tar.xz',  ## This doesn't actually exist (yet).
			BLP.macos_x64: 'dmg',
			BLP.macos_arm64: 'dmg',
			BLP.windows_x64: 'zip',
			BLP.windows_arm64: 'zip',
		}[self]

	####################
	# - PyPi Information
	####################
	@functools.cached_property
	def pypi_arches(self) -> frozenset[str]:
		"""Set of PyPi CPU-architecture tags supported by this BLPlatform.

		Notes:
			PyPi is the official platform for distributing Python dependencies as ex. wheels.
			For example, it is the default source for `pip install *`.

			PyPi has its own conventions for tagging CPU architectures, including the `universal*` tags for MacOS.
			Therefore, a bridge must be built, by asking the following question:

				- Each `BLPlatform` **implicitly** supports a number of CPU architectures.
				- Each Python dependency wheel **implicitly** supports a number of CPU architectures.
				- _What's the overlap?_

			This property answers that question using a hard-coded mapping from each BLPlatform,
			to the set of all PyPi CPU architecture tags that should be considered identical.
		"""
		BLP = BLPlatform
		return {
			BLP.linux_x64: frozenset({'x86_64'}),
			BLP.linux_arm64: frozenset({'aarch64', 'armv7l', 'arm64'}),
			BLP.macos_x64: frozenset({
				'x86_64',
				'universal',
				'universal2',
				'intel',
				'fat3',
				'fat64',
			}),
			BLP.macos_arm64: frozenset({'arm64', 'universal2'}),
			BLP.windows_x64: frozenset({'', 'amd64'}),
			BLP.windows_arm64: frozenset({'arm64'}),
		}[self]

	@functools.cached_property
	def wheel_platform_tag_prefix(self) -> str:
		"""Prefix of compatible wheel platform tags.

		Notes:
			Does not consider `PEP600` references.

		See Also:
			- `PEP600`: https://peps.python.org/pep-0600/
		"""
		BLP = BLPlatform
		return {
			BLP.linux_x64: 'manylinux_',
			BLP.linux_arm64: 'manylinux_',
			BLP.macos_x64: 'macosx_',
			BLP.macos_arm64: 'macosx_',
			BLP.windows_x64: 'win',
			BLP.windows_arm64: 'win',
		}[self]

	####################
	# - Pymarker Information
	####################
	@functools.cached_property
	def pymarker_os_name(self) -> typ.Literal['posix', 'nt']:
		"""Value of `os.name` on the given Blender platform.

		Notes:
			Does not consider `PEP600` references.

		See Also:
			- `PEP600`: https://peps.python.org/pep-0600/
		"""
		P = BLPlatform
		match self:
			case P.linux_x64 | P.linux_arm64 | P.macos_x64 | P.macos_arm64:
				return 'posix'
			case P.windows_x64 | P.windows_arm64:
				return 'nt'

	@functools.cached_property
	def pymarker_platform_machines(self) -> frozenset[str]:
		"""Value of `os.name` on the given Blender platform.

		Notes:
			Does not consider `PEP600` references.

		See Also:
			- `PEP600`: https://peps.python.org/pep-0600/
		"""
		BLP = BLPlatform
		return {
			BLP.linux_x64: frozenset({'x86_64'}),
			BLP.linux_arm64: frozenset({'aarch64', 'armv7l', 'arm64'}),
			BLP.macos_x64: frozenset({'x86_64', 'i386'}),
			BLP.macos_arm64: frozenset({'arm64'}),
			BLP.windows_x64: frozenset({'amd64'}),
			BLP.windows_arm64: frozenset({'arm64'}),
		}[self]

	@functools.cached_property
	def pymarker_platform_system(self) -> typ.Literal['Linux', 'Darwin', 'Windows']:
		"""Value of `platform.system()` on the given Blender platform.

		Notes:
			Does not consider `PEP600` references.

		See Also:
			- `PEP600`: https://peps.python.org/pep-0600/
		"""
		P = BLPlatform
		match self:
			case P.linux_x64 | P.linux_arm64:
				return 'Linux'
			case P.macos_x64 | P.macos_arm64:
				return 'Darwin'
			case P.windows_x64 | P.windows_arm64:
				return 'Windows'

	@functools.cached_property
	def pymarker_sys_platform(self) -> typ.Literal['linux', 'darwin', 'win32']:
		"""Value of `os.name` on the given Blender platform.

		Notes:
			Does not consider `PEP600` references.

		See Also:
			- `PEP600`: https://peps.python.org/pep-0600/
		"""
		P = BLPlatform
		match self:
			case P.linux_x64 | P.linux_arm64:
				return 'linux'
			case P.macos_x64 | P.macos_arm64:
				return 'darwin'
			case P.windows_x64 | P.windows_arm64:
				return 'win32'
