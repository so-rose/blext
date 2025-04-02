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

import functools
import typing as typ

import pydantic as pyd
from frozendict import deepfreeze, frozendict

from blext.utils.pydantic_frozendict import FrozenDict

from .bl_manifest_version import BLManifestVersion
from .bl_platform import BLPlatform
from .bl_version_source import BLVersionSource, BLVersionSources


####################
# - Blender Version
####################
class BLVersion(pyd.BaseModel, frozen=True):
	"""Identifier for a supported version of Blender.

	References:
		- Version Compatibility: <https://developer.blender.org/docs/release_notes/compatibility/>
	"""

	source: BLVersionSource

	# Blender Compatibiltiy
	valid_manifest_versions: frozenset[BLManifestVersion]
	valid_extension_tags: frozenset[str]

	# Platform Compatibility
	valid_bl_platforms: frozenset[BLPlatform]
	min_glibc_version: tuple[int, int]
	min_macos_version: tuple[int, int]

	# Python Compatibility
	py_sys_version: tuple[int, int, int, str, int]
	valid_python_tags: frozenset[str]
	valid_abi_tags: frozenset[str]

	# Markers
	pymarker_extras: frozenset[str]
	pymarker_implementation_name: str
	pymarker_platform_python_implementation: str

	# Bundled site-packages
	vendored_site_packages: FrozenDict[str, str]

	####################
	# - Version String
	####################
	@functools.cached_property
	def version(self) -> str:
		"""This Blender version as a string.

		Warnings:
			**Do not parse** in hopes of learning anything about where this Blender version came from.

			Very little can be presumed about this string.
			It could be a nice version tuple, a raw `SHA256` commit ID, a special buildbot identifier, or something totally different.
		"""
		return self.source.version

	@functools.cached_property
	def max_manifest_version(self) -> BLManifestVersion:
		"""The latest supported Blender manifest version."""
		return sorted(
			self.valid_manifest_versions,
			key=lambda el: el.semantic_version,
		)[-1]

	####################
	# - Python Marker Environment
	####################
	def pymarker_encoded_package_extras(self, pkg_name: str) -> frozenset[str]:
		"""Encode the name of a pymarker `extra`, corresponding to a given package name.

		Warnings:
			Compared to the keys of `[project.optional-dependencies]` in `pyproject.toml`, this property uses `-` instead of `_`.
			This includes a transformation of `pkg_name` from use of `_`, to use of `-`.

			This matches how the `extra` is defined in `uv.lock`.

		Notes:
			`blext` uses different `[project.optional-dependencies]` to encode packages whose versions differ across versions of Blender / are directly vendored by Blender.
			As a result, `uv` automatically guarantees that any other dependencies one may add are compatible with all of the Blender versions supported by the extension.

			However, by default, `[project.optional-dependencies]` are not allowed to conflict.
			To work around this, one can declare the following to `uv`:

			```toml
			[tool.uv]
			conflicts = [
				[
					{ extra = "bl4_2" },
					{ extra = "bl4_3" },
					{ extra = "bl4_4" },
				],
			]
			```

			However, in `scipy`'s `uv.lock` markers, one may now see something like
			```toml
			[[package]]
			name = "scipy"
			version = "1.15.1"
			source = { registry = "https://pypi.org/simple" }
			dependencies = [
				{ name = "numpy", version = "1.24.3", source = { registry = "https://pypi.org/simple" }, marker = "extra == 'extra-11-simple-proj-bl4-2' or extra == 'extra-11-simple-proj-bl4-3'" },
				{ name = "numpy", version = "1.26.4", source = { registry = "https://pypi.org/simple" }, marker = "extra == 'extra-11-simple-proj-bl4-4' or (extra == 'extra-11-simple-proj-bl4-2' and extra == 'extra-11-simple-proj-bl4-3') or (extra != 'extra-11-simple-proj-bl4-2' and extra != 'extra-11-simple-proj-bl4-3')" },
			]
			```

			When a non-optional package (ex. `scipy`) depends on a package defined _only_ in one of the mutually exclusive optional dependencies (ex. `numpy`), `uv` seems to generate new `extra` names like:
			- `extra-11-simple-proj-bl4-3`
			- `extra-11-simple-proj-bl4-4`
			- `extra-{len(pkg_name)}-{pkg_name}-{pymarker_extra}`

			Presumably, this prevents name-conflicts.

		References:
			- `uv`'s `encode_package_extra()`: <https://github.com/astral-sh/uv/blob/3d946027841ac949b9ecfd5ceaeec721836ee555/crates/uv-resolver/src/universal_marker.rs#L499>
			- `packaging.markers` Environment Evaluation: <https://github.com/pypa/packaging/blob/main/src/packaging/markers.py#L204>
		"""
		pkg_name = pkg_name.replace('_', '-')
		return frozenset(
			{
				f'extra-{len(pkg_name)}-{pkg_name}-{pymarker_extra}'
				for pymarker_extra in self.pymarker_extras
			}
		)

	@functools.cached_property
	def pymarker_implementation_version(self) -> str:
		"""Value of `sys.implementation.version` in this Blender version.

		Reference:
			- Official Derivation of `implementation_version`: <https://peps.python.org/pep-0508/#environment-markers>

		"""
		major, minor, patch, release_kind, serial = self.py_sys_version

		implementation_version = f'{major}.{minor}.{patch}'
		if release_kind != 'final':
			implementation_version += release_kind[0] + str(serial)

		return implementation_version

	def pymarker_environments(
		self,
		*,
		pkg_name: str | None = None,
	) -> frozendict[BLPlatform, tuple[frozendict[str, str], ...]]:
		"""All supported marker environments, indexed by `BLPlatform`.

		Warnings:
			Wheels that utilize `platform_release` marker dependencies are incompatible with Blender extensions.

			This is because there's no way to predict the user's exact `platform_release` when preparing extension wheels.

		Notes:
			Each element contains the following:

			- `implementation_name`: Always `'cpython'`, as Blender only supports the "CPython" Python interpreter.
				- **Source**: Clone of from `sys.implementation.name`.
			- `implementation_version`: Derived from each valid Blender version.
				- **Source**: Derived from the target's `sys.implementation.version`. See the [official environment markers reference](https://peps.python.org/pep-0508/#environment-markers) for an example of code that does this.
			- `os_name`: Derived from each valid `extyp.BLPlatform`.
			- `platform_machine`: Derived from each valid `extyp.BLPlatform`.
			- `platform_release`: Always empty-string, denoting "undefined".
				- **Source**: There's no way to know this in advance for vendored dependencies. It's wildly specific.
			- `platform_python_implementation`: Always `'CPython'`, as Blender only supports the "CPython" Python interpreter.
			- `sys_platform`: Derived from each valid `BLVersion`.
				- **Source**: Derived from target's `sys.platform`: <https://docs.python.org/3/library/sys.html#sys.platform>

		See Also:
			- Official Environment Marker Grammer: https://packaging.python.org/en/latest/specifications/dependency-specifiers/#environment-markers
			- Reference for `packaging.markers.Environment`: <https://packaging.pypa.io/en/stable/markers.html#packaging.markers.Environment>
		"""
		major, minor, patch, *_ = self.py_sys_version
		pymarker_platform_machines: dict[BLPlatform, list[str]] = {
			bl_platform: list(bl_platform.pymarker_platform_machines)
			for bl_platform in self.valid_bl_platforms
		}

		_initial_frozenset: frozenset[str] = frozenset()
		pymarker_environments = {
			bl_platform: [
				{
					'implementation_name': self.pymarker_implementation_name,
					'implementation_version': self.pymarker_implementation_version,
					'os_name': bl_platform.pymarker_os_name,
					'platform_machine': platform_machine,
					'platform_release': '',
					'platform_system': bl_platform.pymarker_platform_system,
					'python_full_version': f'{major}.{minor}.{patch}',
					'platform_python_implementation': self.pymarker_platform_python_implementation,
					'python_version': f'{major}.{minor}',
					'sys_platform': bl_platform.pymarker_sys_platform,
					'extra': pymarker_extra,
				}
				for platform_machine in pymarker_platform_machines[bl_platform]
				for pymarker_extra in (
					self.pymarker_extras
					| (
						_initial_frozenset
						if pkg_name is None
						else self.pymarker_encoded_package_extras(pkg_name)
					)
				)
			]
			for bl_platform in self.valid_bl_platforms
		}
		return deepfreeze(pymarker_environments)  # pyright: ignore[reportAny]

	####################
	# - "Smooshing"
	####################
	def is_smooshable_with(
		self,
		other: typ.Self,
		*,
		ext_bl_platforms: frozenset[BLPlatform] | None = None,
		ext_wheels_python_tags: frozenset[str] | None = None,
		ext_wheels_abi_tags: frozenset[str] | None = None,
		ext_tags: frozenset[str] | None = None,
	) -> bool:
		"""Will an extension that works with one version, also work with the other?

		Parameters:
			other: The candidate for smooshing with `self`.
			ext_bl_platforms: Blender platforms supported by the extension.
				- When given, `valid_bl_platforms` on `self` and `other` must merely be non-strict supersets of this.
			ext_wheels_python_tags: All valid Python tags given by all extension wheels.
				- When given, `valid_python_tags` on `self` and `other` must merely be non-strict supersets of this.
				- Extensions without wheels will have this as `{}`, causing this check to always return `True`.
			ext_wheels_abi_tags: All valid ABI tags given by all extension wheels.
				- When given, `valid_abi_tags` on `self` and `other` must merely be non-strict supersets of this.
				- Extensions without wheels will have this as `none`, causing this check to always return `True` (since all `BLVersion`s must support `none`).
			ext_tags: All extension tags declared by the extension.
				- When given, `valid_extension_tags` on `self` and `other` must merely be non-strict supersets of this.
		"""
		return (
			# Must have at least one blender_manifest.toml schema version in common.
			## - It'd be quite impossible to make "one extension for both" without this.
			len(self.valid_manifest_versions & other.valid_manifest_versions) >= 1
			# Valid BLPlatforms must match.
			## - May be ignored if all *extension*-supported BLPlatforms are supported by both.
			## - NOTE: Each extension BLPlatform must work on at least one BLVersion.
			and (
				self.valid_bl_platforms == other.valid_bl_platforms
				if ext_bl_platforms is None
				else (
					ext_bl_platforms.issubset(self.valid_bl_platforms)
					and ext_bl_platforms.issubset(other.valid_bl_platforms)
				)
			)
			# Python tags (aka. Python versions) must match.
			## - Guarantees that any Python code that works on one, works on the other.
			and (
				self.valid_python_tags == other.valid_python_tags
				if ext_wheels_python_tags is None
				else (
					ext_wheels_python_tags.issubset(self.valid_python_tags)
					and ext_wheels_python_tags.issubset(other.valid_python_tags)
				)
			)
			# ABI tags must match.
			## - Guarantees that any wheel that works on one, works on the other.
			## - May be ignored if all extension wheel ABI tags are supported by both.
			and (
				self.valid_abi_tags == other.valid_abi_tags
				if ext_wheels_abi_tags is None
				else (
					ext_wheels_abi_tags.issubset(self.valid_abi_tags)
					and ext_wheels_abi_tags.issubset(other.valid_abi_tags)
				)
			)
			# Available / valid extension tags must match.
			## - Guarantees that any extension (info) tag parseable by one Blender, parses on the other.
			## - May be ignored if all extension (info) tags are supported by both.
			and (
				self.valid_extension_tags == other.valid_extension_tags
				if ext_tags is None
				else (
					ext_tags.issubset(self.valid_extension_tags)
					and ext_tags.issubset(other.valid_extension_tags)
				)
			)
		)

	def smoosh_with(
		self,
		other: typ.Self,
		ext_bl_platforms: frozenset[BLPlatform] | None = None,
		ext_wheels_python_tags: frozenset[str] | None = None,
		ext_wheels_abi_tags: frozenset[str] | None = None,
		ext_tags: frozenset[str] | None = None,
	) -> typ.Self:
		"""Chunk with another `BLVersion`, forming a new `BLVersion` encapsulating both."""
		if self.is_smooshable_with(
			other,
			ext_bl_platforms=ext_bl_platforms,
			ext_wheels_python_tags=ext_wheels_python_tags,
			ext_wheels_abi_tags=ext_wheels_abi_tags,
			ext_tags=ext_tags,
		):
			return BLVersion(  # pyright: ignore[reportReturnType]
				source=BLVersionSources(
					# Every smoosh increments the "smoosh list", with order-preservation.
					sources=(
						(
							self.source.sources
							if isinstance(self.source, BLVersionSources)
							else frozenset({self.source})
						)
						| (
							other.source.sources
							if isinstance(other.source, BLVersionSources)
							else frozenset({other.source})
						)
					)
				),
				valid_manifest_versions=(
					self.valid_manifest_versions & other.valid_manifest_versions
				),
				valid_extension_tags=(
					self.valid_extension_tags & other.valid_extension_tags
				),
				valid_bl_platforms=(self.valid_bl_platforms & other.valid_bl_platforms),
				min_glibc_version=self.min_glibc_version,  ## TODO: Choose smallest.
				min_macos_version=self.min_macos_version,  ## TODO: Choose smallest.
				py_sys_version=self.py_sys_version,  ## TODO: Choose "smallest".
				valid_python_tags=(self.valid_python_tags & other.valid_python_tags),
				valid_abi_tags=(self.valid_abi_tags & other.valid_abi_tags),
				pymarker_extras=self.pymarker_extras | other.pymarker_extras,
				pymarker_implementation_name=self.pymarker_implementation_name,
				pymarker_platform_python_implementation=self.pymarker_platform_python_implementation,
				vendored_site_packages=self.vendored_site_packages,
			)

		msg = "Tried to 'smoosh' two incompatible BLVersions together."
		raise ValueError(msg)
