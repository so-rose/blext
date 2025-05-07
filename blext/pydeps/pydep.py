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

"""Implements `PyDep` and `PyDepMarker."""

import functools
import re
import typing as typ

import annotated_types as atyp
import packaging.utils
import packaging.version
import pydantic as pyd
import semver.version
from frozendict import frozendict

from blext import extyp
from blext.utils.lru_method import lru_method
from blext.utils.pydantic_frozendict import FrozenDict

from .pydep_marker import PyDepMarker
from .pydep_wheel import PyDepWheel

####################
# - Constants
####################
_EMPTY_FROZENSET_STR = frozenset[str]()

RE_PYDEP_NAME = re.compile(r'^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$', re.IGNORECASE)
RE_PYDEP_VERSION = re.compile(
	r'^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$'
)


def match_pydep_name_regex(name: str) -> bool:
	"""Match a candidate string for `PyDep.name` to its name."""
	return RE_PYDEP_NAME.match(name) is not None


def match_pydep_version_regex(name: str) -> bool:
	"""Match a candidate string for `PyDep.name` to its name."""
	return RE_PYDEP_VERSION.match(name) is not None


####################
# - Class
####################
class PyDep(pyd.BaseModel, frozen=True):
	"""Representation of a valid Python dependency.

	Attributes:
		name: The name of the Python dependency.
		version: The version string of the Python dependency.
		registry: The registry URL where distributions of this Python dependency can be found.
		wheels: All wheels associated with this Python dependency.
		markers: All markers

	"""

	name: typ.Annotated[
		str,
		atyp.Predicate(match_pydep_name_regex),
	]
	version_string: typ.Annotated[
		str,
		atyp.Predicate(match_pydep_version_regex),
	]
	registry: pyd.HttpUrl
	wheels: frozenset[PyDepWheel]

	deps: FrozenDict[
		typ.Annotated[
			str,
			atyp.Predicate(match_pydep_name_regex),
		],
		PyDepMarker | None,
	]

	####################
	# - Properties
	####################
	@functools.cached_property
	def version(self) -> packaging.version.Version:
		"""Standardized `packging.version.Version`, derived from `self.version_string`."""
		return packaging.version.Version(self.version_string)

	####################
	# - Wheel Selection
	####################
	@lru_method()
	def semivalid_wheels_for(
		self,
		*,
		bl_platform: extyp.BLPlatform,
		valid_python_tags: frozenset[str],
		valid_abi_tags: frozenset[str],
	) -> frozenset[PyDepWheel]:
		"""Select all wheels that implement this `PyDep`, which work with any OS version of the given Python environment.

		Notes:
			These wheels are considered "semivalid", since they **do not** take the minimum `glibc` or `macos` version of the target environment into account.

			However, when solving dependency problems, all wheels here are theoretically otherwise OK.
			Therefore, it makes sense to consider this subset before further filtering.

		Parameters:
			bl_platform: The target environment's Blender platform.
			valid_python_tags: The supported Python interpreter tags of the target environment.
			valid_abi_tags: The supported Python ABI tags of the target environment.

		Returns:
			All wheels compatible with:

				- The given `BLPlatform` of the target environment.
				- One of the given `valid_python_tags`.
				- One of the given `valid_abi_tags`.
		"""
		return frozenset(
			wheel
			for wheel in self.wheels
			# The wheel must work in an environment that supports the given python tags.
			if wheel.works_with_python_tags(valid_python_tags)
			# The wheel must work in an environment that supports the given ABI tags.
			and wheel.works_with_abi_tags(valid_abi_tags)
			# The wheel must work for any OS version of the given BLPlatform.
			and wheel.works_with_bl_platform(
				bl_platform=bl_platform,
				min_glibc_version=None,
				min_macos_version=None,
			)
		)

	@lru_method()
	def valid_wheels_for(
		self,
		*,
		bl_platform: extyp.BLPlatform,
		valid_python_tags: frozenset[str],
		valid_abi_tags: frozenset[str],
		min_glibc_version: semver.version.Version,
		min_macos_version: semver.version.Version,
	) -> frozenset[PyDepWheel]:
		"""Select all wheels that implement this `PyDep`, which work with the given Python environment.

		Notes:
			These wheels are considered "valid", since they **do** take the minimum `glibc` and/or `macos` version of the target environment into account.

		Parameters:
			bl_platform: The target environment's Blender platform.
			valid_python_tags: The supported Python interpreter tags of the target environment.
			valid_abi_tags: The supported Python ABI tags of the target environment.
			min_glibc_version: The minimum `glibc` version of the target environment.
				_Ignored if the target environment is not Linux-based._
			min_macos_version: The minimum `macos` version of the target environment.
				_Ignored if the target environment is not MacOS-based._

		Returns:
			All wheels compatible with:

				- The given `BLPlatform` of the target environment.
				- One of the given `valid_python_tags`.
				- One of the given `valid_abi_tags`.
				- An OS with at least `min_glibc_version` (Linux) or `min_macos_version` (MacOS), if relevant (Windows ignores both).

			**Any wheel** returned by this method will work in the given Python environment.
			In general, however, it's best to select the wheel with the largest `glibc` / `macos` version, as this is likely to provide the widest and/or most expected feature set for the user.
		"""
		return frozenset(
			wheel
			for wheel in self.semivalid_wheels_for(
				bl_platform=bl_platform,
				valid_python_tags=valid_python_tags,
				valid_abi_tags=valid_abi_tags,
			)
			# The wheel must work for the constrained OS version of the given BLPlatform.
			if wheel.works_with_bl_platform(
				bl_platform=bl_platform,
				min_glibc_version=min_glibc_version,
				min_macos_version=min_macos_version,
			)
		)

	def select_wheel(  # noqa: PLR0913
		self,
		*,
		bl_platform: extyp.BLPlatform,
		valid_python_tags: frozenset[str],
		valid_abi_tags: frozenset[str],
		min_glibc_version: semver.version.Version,
		min_macos_version: semver.version.Version,
		target_descendants: frozenset[str] = _EMPTY_FROZENSET_STR,
		err_msgs: dict[extyp.BLPlatform, list[str]] | None = None,
	) -> PyDepWheel | None:
		"""Select the "best" wheel to implement this `PyDep` in a given Python environment.

		Notes:
			This method essentially selects the "best" wheel from `self.valid_wheels_for(...)`.

			In this context, "best" means "highest OS version" (`min_glibc_version` or `min_macos_version`), since this maximizes the feature available to the user.

		Parameters:
			bl_platform: The target environment's Blender platform.
			valid_python_tags: The supported Python interpreter tags of the target environment.
			valid_abi_tags: The supported Python ABI tags of the target environment.
			min_glibc_version: The minimum `glibc` version of the target environment.
				_Ignored if the target environment is not Linux-based._
			min_macos_version: The minimum `macos` version of the target environment.
				_Ignored if the target environment is not MacOS-based._
			target_descendants: Names of the downstream `PyDep`s that cause this `PyDep` to be included.
				_Only used to prepare an error message._
			err_msgs: Error messages to propagate to the caller by-platform.
				_Only used to prepare an error message._

		Returns:
			All wheels compatible with:

				- The given `BLPlatform` of the target environment.
				- One of the given `valid_python_tags`.
				- One of the given `valid_abi_tags`.
				- An OS with at least `min_glibc_version` (Linux) or `min_macos_version` (MacOS), if relevant (Windows ignores both).

			**Any wheel** returned by this method will work in the given Python environment.
			In general, however, it's best to select the wheel with the largest `glibc` / `macos` version, as this is likely to provide the widest and/or most expected feature set for the user.
		"""
		####################
		# - Step 0: Find All Valid Wheels
		####################
		semivalid_wheels = self.semivalid_wheels_for(
			bl_platform=bl_platform,
			valid_python_tags=valid_python_tags,
			valid_abi_tags=valid_abi_tags,
		)
		valid_wheels = self.valid_wheels_for(
			bl_platform=bl_platform,
			valid_python_tags=valid_python_tags,
			valid_abi_tags=valid_abi_tags,
			min_glibc_version=min_glibc_version,
			min_macos_version=min_macos_version,
		)

		####################
		# - Step 1: Select "Best" Wheel
		####################
		## - Prefer some wheels over others in a platform-specific manner.
		## - For instance, one might want to prefer higher `glibc` versions when available.
		match bl_platform:
			case extyp.BLPlatform.linux_x64 | extyp.BLPlatform.linux_arm64:
				if valid_wheels:
					return sorted(
						valid_wheels,
						key=lambda wheel: wheel.sort_key_preferred_linux,
					)[0]

				## Error Handling
				osver_str = 'glibc'
				min_osver_str = f'{min_glibc_version.major}.{min_glibc_version.minor}'
				semivalid_wheel_osver_strs = {
					semivalid_wheel: (
						f'{semivalid_wheel.min_glibc_version.major}.{semivalid_wheel.min_glibc_version.minor}'
						if semivalid_wheel.min_glibc_version is not None
						else ''
					)
					for semivalid_wheel in semivalid_wheels
				}
				##

			case extyp.BLPlatform.macos_x64 | extyp.BLPlatform.macos_arm64:
				if valid_wheels:
					return sorted(
						valid_wheels,
						key=lambda wheel: wheel.sort_key_preferred_mac,
					)[0]

				## Error Handling
				osver_str = 'macos'
				min_osver_str = f'{min_macos_version.major}.{min_macos_version.minor}'
				semivalid_wheel_osver_strs = {
					semivalid_wheel: (
						f'{semivalid_wheel.min_macos_version.major}.{semivalid_wheel.min_macos_version.minor}'
						if semivalid_wheel.min_macos_version is not None
						else ''
					)
					for semivalid_wheel in semivalid_wheels
				}
				##

			case extyp.BLPlatform.windows_x64 | extyp.BLPlatform.windows_arm64:
				if valid_wheels:
					return sorted(
						valid_wheels,
						key=lambda wheel: wheel.sort_key_preferred_windows,
					)[0]

				## The error assembly must not use osver_str for windows.
				## Trust the process. Or contribute a pull request ;)

		# Collect Errors w/Explanation and Remedies
		errors = [
			f'**{self.name}** not found for `{bl_platform}`.',
			f'> **Extension Supports**: `{osver_str} >= {min_osver_str}`'  # pyright: ignore[reportPossiblyUnboundVariable]
			if not bl_platform.is_windows
			else '>',
			'>',
			'> ----' if not bl_platform.is_windows else '>',
			'> **Rejected Wheels**:'
			if semivalid_wheels
			else '> **Rejected Wheels**: No candidates were found.',
			*(
				[
					f'> - {semivalid_wheel.filename}: `{osver_str} >= {semivalid_wheel_osver_strs[semivalid_wheel]}`'  # pyright: ignore[reportPossiblyUnboundVariable]
					for semivalid_wheel in semivalid_wheels
				]
				if not bl_platform.is_windows
				else []
			),
			'>',
			'> ----',
			'> **Remedies**:',
			f'> 1. **Remove** `{bl_platform}` from `tool.blext.supported_platforms`.',
			f'> 2. **Remove** `{"==".join(next(iter(target_descendants)))}` from `project.dependencies`.'
			if len(target_descendants) == 1
			else f'> 2. **Remove** `{self.name}=={self.version_string}` from `project.dependencies`.',
			f'> 3. **Raise** `{osver_str}` version in `tool.blext.min_{osver_str}_version`.'  # pyright: ignore[reportPossiblyUnboundVariable]
			if semivalid_wheels and not bl_platform.is_windows
			else '>',
			'',
		]
		if err_msgs is not None:
			err_msgs[bl_platform].extend(errors)
			return None

		raise ValueError(*errors)

	####################
	# - Validators
	####################
	@pyd.field_validator('name', mode='after')
	@classmethod
	def normalize_name_field(cls, name: str) -> packaging.utils.NormalizedName:
		"""Normalize the Python dependency name to its standard, comparable form.

		Notes:
			Uses `packaging.utils.canonicalize_name(name, validate=True)` to perform the normalization.

		Parameters:
			cls: This class.
			name: The non-normalized string name of the Python dependency.

		Returns:
			The normalized variant of `name`.

		Raises:
			InvalidName: If `name` is not a valid Python dependency name.

		See Also:
			- PyPa Name Normalization: <https://packaging.python.org/en/latest/specifications/name-normalization/>
			- `packaging.utils`: <https://packaging.pypa.io/en/stable/utils.html#packaging.utils.canonicalize_name>
		"""
		try:
			return packaging.utils.canonicalize_name(name, validate=True)
		except packaging.utils.InvalidName as ex:
			msg = f'Could not create `PyDep` with invalid name: `{name}`.'
			raise ValueError(msg) from ex

	@pyd.field_validator('version_string', mode='after')
	@classmethod
	def normalize_version_field(cls, version_string: str) -> str:
		"""Normalize the Python dependency version string to its standard form.

		Notes:
			Uses `packaging.utils.canonicalize_version(version_string)` to perform the normalization.

		Parameters:
			cls: This class.
			version_string: The non-normalized string version of the Python dependency.

		Returns:
			The normalized variant of `version_string`.

		See Also:
			- PyPa Version Normalization: <https://packaging.python.org/en/latest/specifications/version-specifiers/#appendix-parsing-version-strings-with-regular-expressions>
			- `packaging.utils`: <https://packaging.pypa.io/en/stable/utils.html#packaging.utils.canonicalize_version>
		"""
		return packaging.utils.canonicalize_version(version_string)

	@pyd.field_validator('deps', mode='after')
	@classmethod
	def normalize_deps_names(
		cls, deps: frozendict[str, PyDepMarker | None]
	) -> frozendict[packaging.utils.NormalizedName, PyDepMarker | None]:
		"""Normalize all Python dependency names of this `PyDep`'s own dependencies.

		Notes:
			Uses `packaging.utils.canonicalize_name(name, validate=True)` to perform each normalization.

		Parameters:
			cls: This class.
			deps: The dependencies of this `PyDep`, including any markers, but with non-normalized string names.

		Returns:
			`deps`, but with normalized string names.

		Raises:
			InvalidName: If one of the keys of `deps` is not a valid Python dependency name.

		See Also:
			- PyPa Version Normalization: <https://packaging.python.org/en/latest/specifications/version-specifiers/#appendix-parsing-version-strings-with-regular-expressions>
			- `packaging.utils`: <https://packaging.pypa.io/en/stable/utils.html#packaging.utils.canonicalize_version>
		"""
		normalized_deps = dict[str, PyDepMarker | None]()
		for dep_name, dep_marker in deps.copy().items():
			try:
				normalized_deps[
					packaging.utils.canonicalize_name(dep_name, validate=True)
				] = dep_marker
			except packaging.utils.InvalidName as ex:
				msg = f'Could not parse `dep_name` (`{dep_name}`) of a `PyDep` dependency.'
				raise ValueError(msg) from ex

		return frozendict(normalized_deps)
