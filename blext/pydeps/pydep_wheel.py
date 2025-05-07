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

"""Defines an abstraction for a Blender extension wheel."""

import functools
import hashlib
import re
import string
import typing as typ
from pathlib import Path

import annotated_types as atyp
import packaging.tags
import packaging.utils
import packaging.version
import pydantic as pyd
import semver.version

from blext import extyp

####################
# - Funcs: Validation
####################
_SHA256_STR_LEN = 71
_HEX_DIGITS_SET = frozenset({c for c in string.hexdigits if c.isdigit() or c.islower()})

RE_SHA256_HASH = re.compile(r'^sha256:[0123456789abcdef]{64}$')


def is_valid_sha256_hash(s: str) -> bool:
	"""Whether `s` is a valid `SHA256` hash string.

	Notes:
		A valid `SHA256` string starts with `sha256:`, is exactly 71 characters long, and is composed entirely of hexadecimal digits after the `:`.

	Parameters:
		s: The string to test for being a valid `SHA256` hash string.

	Returns:
		Whether `s` is a valid `SHA256` hash string.
	"""
	return (
		s.startswith('sha256:')
		and len(s) == _SHA256_STR_LEN
		and set(s[7:]).issubset(_HEX_DIGITS_SET)
	)


####################
# - Class: Python Dependency Wheel
####################
class PyDepWheel(pyd.BaseModel, frozen=True):
	"""Representation of a (remote) Python dependency."""

	url: pyd.HttpUrl
	registry: pyd.HttpUrl

	hash: typ.Annotated[
		str,
		atyp.Predicate(is_valid_sha256_hash),
	]
	size: pyd.ByteSize

	@functools.cached_property
	def filename(self) -> str:
		"""Parse the filename of the wheel file."""
		if self.url.path is not None:
			url_parts = self.url.path.split('/')
			if url_parts[-1].endswith('.whl'):
				return url_parts[-1]

		msg = f"Wheel filename could not be found in URL '{self.url}'"
		raise RuntimeError(msg)

	####################
	# - Wheel Properties
	####################
	@functools.cached_property
	def _parsed_wheel_filename(
		self,
	) -> tuple[
		packaging.utils.NormalizedName,
		packaging.version.Version,
		tuple[()] | tuple[int, str],
		frozenset[packaging.tags.Tag],
	]:
		"""Parse the wheel filename for information.

		Raises:
			packaging.utils.InvalidWheelFilename: When `self.filename` is an invalid wheel filename.
		"""
		return packaging.utils.parse_wheel_filename(self.filename)

	@property
	def pydep_name(self) -> packaging.utils.NormalizedName:
		"""The name of the Python dependency provided by this wheel."""
		return self._parsed_wheel_filename[0]

	@property
	def pydep_version(self) -> packaging.version.Version:
		"""The version of the Python dependency provided by this wheel."""
		return self._parsed_wheel_filename[1]

	@property
	def build_tag(self) -> tuple[int, str] | None:
		"""The build tag associated with this wheel."""
		build_tag = self._parsed_wheel_filename[2]
		if build_tag == ():
			return None
		return build_tag  # pyright: ignore[reportReturnType]
		## NOTE: pyright not narrowing tuple[()] when != () may be a bug.

	@property
	def tags(self) -> frozenset[packaging.tags.Tag]:
		"""All environment tags provided by this wheel.

		Notes:
			Each tag declares compatibility with one Python interpreter, ABI target, and platform.

			Wheels may declare multiple tags, by utilizing so-called "compressed tag sets".

		See Also:
			- Platform Compatibility Tags: <https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/>
			- Compressed Tag Sets: <https://peps.python.org/pep-0425/#compressed-tag-sets>
		"""
		return self._parsed_wheel_filename[3]

	####################
	# - Platform Tag Elements
	####################
	@functools.cached_property
	def python_tags(self) -> frozenset[str]:
		"""The Python tags of the wheel."""
		return frozenset(tag.interpreter for tag in self.tags)

	@functools.cached_property
	def abi_tags(self) -> frozenset[str]:
		"""The ABI tags of the wheel."""
		return frozenset(tag.abi for tag in self.tags)

	@functools.cached_property
	def platform_tags(self) -> frozenset[str]:
		"""The platform tags of the wheel.

		Notes:
			Legacy `manylinux` tags (such as `2014`) are normalized to their
			explicit `PEP600` equivalents (ex. `2014 -> 2_17`).

			This is done automatically by `packaging`

			This is done to avoid irregularities in how `glibc` versions are parsed
			for `manylinux` wheels in later methods.

		See Also:
			- `PEP600`: https://peps.python.org/pep-0600/

		"""
		return frozenset(tag.platform for tag in self.tags)

	####################
	# - Platform Support: Overview
	####################
	@functools.cached_property
	def supports_all_platforms(self) -> bool:
		"""Whether this wheel supports all platforms."""
		return any(platform_tag == 'any' for platform_tag in self.platform_tags)

	@functools.cached_property
	def supports_linux(self) -> bool:
		"""Whether this wheel supports some version of Linux on some architecture."""
		return self.supports_all_platforms or any(
			platform_tag.startswith('manylinux_') for platform_tag in self.platform_tags
		)

	@functools.cached_property
	def supports_macos(self) -> bool:
		"""Whether this wheel supports some version of Mac OS on some architecture."""
		return self.supports_all_platforms or any(
			platform_tag.startswith('macos_') for platform_tag in self.platform_tags
		)

	@functools.cached_property
	def supports_windows(self) -> bool:
		"""Whether this wheel supports Windows on some architecture."""
		return self.supports_all_platforms or any(
			platform_tag.startswith('win') for platform_tag in self.platform_tags
		)

	@functools.cached_property
	def supports_win32(self) -> bool:
		"""Whether this wheel supports Windows on some architecture."""
		return self.supports_all_platforms or (
			self.supports_windows
			and any(platform_tag == 'win32' for platform_tag in self.platform_tags)
		)

	####################
	# - Platform Support: Narrowed
	####################
	@functools.cached_property
	def min_glibc_version(self) -> semver.version.Version | None:
		"""Minimum GLIBC versions supported by this wheel.

		Notes:
			- The smallest available GLIBC version indicates the minimum GLIBC support for this wheel.
			- Non-`manylinux` platform tags will always map to `None`.
		"""
		manylinux_platform_tags = [
			platform_tag
			for platform_tag in self.platform_tags
			if platform_tag.startswith('manylinux_')
		]
		if manylinux_platform_tags:
			glibc_versions = tuple(
				semver.version.Version(
					*(
						int(glibc_version_part)
						for glibc_version_part in manylinux_platform_tag.removeprefix(
							'manylinux_'
						).split('_')[:2]
					)
				)
				for manylinux_platform_tag in manylinux_platform_tags
			)
			return min(glibc_versions)
		return None

	@functools.cached_property
	def min_macos_version(self) -> semver.version.Version | None:
		"""Minimum MacOS versions supported by this wheel.

		Notes:
			- The smallest available MacOS version indicates the minimum GLIBC support for this wheel.
			- Non-`macosx` platform tags will always map to `None`.
		"""
		macos_platform_tags = [
			platform_tag
			for platform_tag in self.platform_tags
			if platform_tag.startswith('macosx_')
		]
		if macos_platform_tags:
			macos_versions = tuple(
				semver.version.Version(
					*(
						int(macos_version_part)
						for macos_version_part in macos_platform_tag.removeprefix(
							'macosx_'
						).split('_')[:2]
					)
				)
				for macos_platform_tag in macos_platform_tags
			)
			return min(macos_versions)
		return None

	####################
	# - Sorting Keys
	####################
	@functools.cached_property
	def sort_key_size(self) -> int:
		"""Priority to assign to this wheel sorting by size.

		Notes:
			- Higher values will sort later in the list.
			- When `self.size is None`, then the "size" will be set to 0.
		"""
		return int(self.size)

	@functools.cached_property
	def sort_key_preferred_linux(self) -> int:
		"""Priority to assign to this wheel when selecting one of several Linux wheels.

		Notes:
			The smallest value will be chosen as the preferred wheel.
		"""
		if self.min_glibc_version is not None:
			return -(
				100_000 * self.min_glibc_version.major + self.min_glibc_version.minor
			)
		return 0

	@functools.cached_property
	def sort_key_preferred_mac(self) -> int:
		"""Priority to assign to this wheel when selecting one of several MacOS wheels.

		Notes:
			The smallest value will be chosen as the preferred wheel.
		"""
		if self.min_macos_version is not None:
			return -(
				100_000 * self.min_macos_version.major + self.min_macos_version.minor
			)
		return 0

	@functools.cached_property
	def sort_key_preferred_windows(self) -> int:
		"""Priority to assign to this wheel when selecting one of several Windows wheels.

		Notes:
			The smallest value will be chosen as the preferred wheel.
		"""
		return sum(
			{'any': 2, 'win_arm64': 0, 'win_amd64': 0, 'win32': 1}[platform_tag]
			for platform_tag in self.platform_tags
		)

	####################
	# - Match BLPlatform
	####################
	def works_with_bl_platform(  # noqa: PLR0911
		self,
		bl_platform: extyp.BLPlatform,
		*,
		min_glibc_version: semver.version.Version | None,
		min_macos_version: semver.version.Version | None,
	) -> bool:
		"""Whether this wheel ought to run on the given platform.

		Parameters:
			bl_platform: The Blender platform that the wheel would be run on.
			min_glibc_version: The minimum version of `glibc` available.
				- **Note**: Only relevant for Linux-based `bl_platform`s.
			min_macos_version: The minimum version of `macos` available.
				- **Note**: Only relevant for MacOS-based `bl_platform`s.

		Notes:
			`extyp.BLPlatform` only denotes a _partial_ set of compatibility constraints,
			namely, particular OS / CPU architecture combinations.

			It does **not** a sufficient set of compatibility constraints to be able to say,
			for instance, "this wheel will work with any Linux version of Blender".

			A version of Blender versions comes with a Python runtime environment that imposes
			very important constraints such as:
			- Supported Python tags.
			- Supported ABI tags.

			To deduce final wheel compatibility, _both_ the BLPlatform _and_ the information derived
			from the Blender version must be checked.
		"""
		####################
		# - Step 0: Check 'any'
		####################
		if self.supports_all_platforms:
			return True

		####################
		# - Step 1: Check Architecture and OS
		####################
		## - This information is contained in the prefix and suffix of each platform tag.

		# At least one platform tag must end with one of bl_platform's valid architectures.
		arch_matches = any(
			platform_tag.endswith(pypi_arch)
			for platform_tag in self.platform_tags
			for pypi_arch in bl_platform.pypi_arches
		)

		# Workaround to support explicit 'win32' platform tags on all Windows versions.
		if (
			not arch_matches
			and bl_platform is extyp.BLPlatform.windows_x64
			and self.supports_win32
		):
			arch_matches = True

		# At least one platform tag must start with one of bl_platform's valid wheel prefixes.
		os_matches = any(
			platform_tag.startswith(bl_platform.wheel_platform_tag_prefix)
			for platform_tag in self.platform_tags
		)

		if not (arch_matches and os_matches):
			return False

		####################
		# - Step 2: Check OS Version
		####################
		## - The minimum `glibc` / `macos` versions must be checked, if applicable.

		match bl_platform:
			case extyp.BLPlatform.linux_x64 | extyp.BLPlatform.linux_arm64 if (
				self.min_glibc_version is not None
			):
				if min_glibc_version is not None:
					return self.min_glibc_version <= min_glibc_version
				return True

			case extyp.BLPlatform.macos_x64 | extyp.BLPlatform.macos_arm64 if (
				self.min_macos_version is not None
			):
				if min_macos_version is not None:
					return self.min_macos_version <= min_macos_version
				return True

			case extyp.BLPlatform.windows_x64 | extyp.BLPlatform.windows_arm64:
				return True

			case _:
				msg = "For either Linux or Mac, either the given or the wheel's minimum OS version was `None`. This is a bug in `blext`."
				raise RuntimeError(msg)

	####################
	# - Wheel Validation
	####################
	def works_with_python_tags(self, valid_python_tags: frozenset[str]) -> bool:
		"""Does this wheel work with a runtime that supports `python_tags`?

		Notes:
			This method doesn't guarantee directly that the wheel will run.
			It only guarantees that there is no mismatch in Python tags between
			what the environment supports, and what the wheel supports.

		Parameters:
			valid_python_tags: List of Python tags supported by a runtime environment.

		Returns:
			Whether the Python tags of the environment, and the wheel, are compatible.
		"""
		return len(valid_python_tags & self.python_tags) > 0

	def works_with_abi_tags(self, valid_abi_tags: frozenset[str]) -> bool:
		"""Does this wheel work with a runtime that supports `abi_tags`?

		Notes:
			- It is very strongly recommended to always pass `"none"` as one of the `abi_tags`,
				since this is the ABI tag of pure-Python wheels.
			- This method doesn't guarantee directly that the wheel will run.
				It only guarantees that there is no mismatch in Python ABI tags between
				what the environment supports, and what the wheel supports.

		Parameters:
			valid_abi_tags: List of ABI tags supported by a runtime environment.

		Returns:
			Whether the Python tags of the environment, and the wheel, are compatible.
		"""
		return len(valid_abi_tags & self.abi_tags) > 0

	def is_download_valid(self, wheel_path: Path) -> bool:
		"""Check whether a downloaded file is, in fact, this wheel.

		Notes:
			Implemented by comparing the file hash to the expected hash.

		Raises:
			ValueError: If the hash digest of `wheel_path` does not match `self.hash`.
		"""
		if wheel_path.is_file():
			with wheel_path.open('rb', buffering=0) as f:
				file_digest = hashlib.file_digest(f, 'sha256').hexdigest()

			return 'sha256:' + file_digest == self.hash
		return False

	####################
	# - Display
	####################
	@functools.cached_property
	def pretty_bl_platforms(self) -> str:
		"""Retrieve prettified, unfiltered `bl_platforms` for this wheel."""
		if 'any' in self.platform_tags:
			return 'all'

		return ', '.join(
			sorted([
				bl_platform
				for bl_platform in extyp.BLPlatform
				if self.works_with_bl_platform(
					bl_platform=bl_platform,
					min_glibc_version=None,
					min_macos_version=None,
				)
			])
		)
