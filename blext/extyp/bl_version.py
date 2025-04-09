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

import datetime as dt
import functools
import typing as typ

import packaging.version
import pydantic as pyd
from frozendict import deepfreeze, frozendict

from blext.utils.pydantic_frozendict import FrozenDict

from .bl_manifest_version import BLManifestVersion
from .bl_platform import BLPlatform


####################
# - Blender Version
####################
@functools.total_ordering
class BLVersion(pyd.BaseModel, frozen=True):
	"""Identifier for a supported version of Blender.

	References:
		- Version Compatibility: <https://developer.blender.org/docs/release_notes/compatibility/>
	"""

	# General Properties
	released_on: dt.datetime
	blender_version_min: tuple[int, int, int]
	blender_version_max: tuple[int, int, int]

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
	vendored_site_package_strs: FrozenDict[str, str]

	####################
	# - Key Information
	####################
	@functools.cached_property
	def max_manifest_version(self) -> BLManifestVersion:
		"""The latest supported Blender manifest version."""
		return sorted(
			self.valid_manifest_versions,
			key=lambda el: el.semantic_version,
		)[-1]

	@functools.cached_property
	def vendored_site_packages(
		self,
	) -> frozendict[str, packaging.version.Version]:
		"""All dependencies vendored by this Blender version."""
		return frozendict({
			pkg_name: packaging.version.Version(pkg_version_str)
			for pkg_name, pkg_version_str in self.vendored_site_package_strs.items()
		})

	####################
	# - Pretty Version
	####################
	@functools.cached_property
	def pretty_version(self) -> str:  # noqa: C901, PLR0912
		"""This Blender version as a string.

		Notes:
			**Do not parse** in hopes of learning anything about where this Blender version came from.

			Very little can be presumed about this string.
			It could be a nice version tuple, a raw `SHA256` commit ID, a special buildbot identifier, or something totally different.
		"""
		v0 = self.blender_version_min
		v1 = self.blender_version_max
		if not v0 < v1:
			msg = f"Somehow, Palpa... `blender_version_min >= blender_version_max`, I mean ({self.blender_version_min} >= {self.blender_version_max}). Anyway, this shouldn't happen, so please report this bug :)"
			raise RuntimeError(msg)

		v0_M_m_str = '_'.join(str(v) for v in v0[:2])
		v1_M_mm1_str = '_'.join(str(v) for v in (v1[0], v1[1] - 1))

		v0_M_m_p_str = '_'.join(str(v) for v in v0)
		v1_M_m_p_str = '_'.join(str(v) for v in v1)
		v1_M_m_pm1_str = '_'.join(str(v) for v in (*v1[:2], v1[2] - 1))

		v0_str = f'bl{v0_M_m_p_str}'
		v1_str = f'bl{v1_M_m_p_str}'

		####################
		# - Step 0: Untangle v0
		####################
		# v0: Detect Major Version Ranges
		## If upper is larger in M or m, then always use M.m for lower bound.
		if (v0[0] < v1[0] or (v0[0] == v1[0] and v0[1] < v1[1])) and v0[2] == 0:
			v0_str = f'bl{v0_M_m_str}'

		####################
		# - Step 1: Untangle v1
		####################
		# When the major vesion skips by >0...
		if v0[0] < v1[0]:
			# ...and the patch version is 0...
			if v1[2] == 0:
				# ...and the minor version is 0?
				## THEN, the end should just be that major version.
				if v1[1] == 0:  # noqa: SIM108
					v1_str = f'bl{v1[0]}'

				# ...and the minor version is >0?
				## THEN, the end should be M.(m-1).
				else:
					v1_str = f'bl{v1_M_mm1_str}'

			# ...and the patch version is >0?
			## THEN, the end should be M.m.(p-1).
			else:
				v1_str = f'bl{v1_M_m_pm1_str}'

		# When the major versions are identical...
		else:  # noqa: PLR5501
			# ...and the patch version is 0...
			if v1[2] == 0:
				# NOTE: M.m.p versions cannot all be identical, so no check for this.

				# ...and the minor version skipped by 1?
				## THEN, don't use an an end string at all.
				if v0[1] == v1[1] - 1:
					v1_str = None

				# ...and the minor version skipped by >1?
				## THEN, use M.(m-1)
				elif v0[1] < v1[1]:
					v1_str = f'bl{v1_M_mm1_str}'

			# ...and the patch version is >0...
			else:  # noqa: PLR5501
				# ...and the minor versions are identical...
				if v0[1] == v1[1]:
					# ...and the patch version skipped by 1?
					## THEN, don't use an end string at all.
					if v0[2] == v1[2] - 1:  # noqa: SIM108
						v1_str = None

					# ...and the patch version skipped by >1?
					## THEN, use M.m.(p-1).
					else:
						v1_str = f'bl{v1_M_m_pm1_str}'

				# ...and the minor version skipped by >0?
				## THEN, use M.m.(p-1).
				else:
					v1_str = f'bl{v1_M_m_pm1_str}'

		# NOTE: ^ is not designed as an optimal construction.
		## It is designed as a comprehensible construction.

		# Render Pretty Version Range
		if v1_str is None:
			return v0_str
		return f'{v0_str}-{v1_str}'

	####################
	# - Python Marker Environment
	####################
	def pymarker_encoded_package_extras(self, pkg_name: str) -> frozenset[str]:
		"""Encode the name of a pymarker `extra`, corresponding to a given package name.

		Notes:
			Compared to the keys of `[project.optional-dependencies]` in `pyproject.toml`, this property uses `-` instead of `_`.
			This includes a transformation of `pkg_name` from use of `_`, to use of `-`.

			This matches how the `extra` is defined in `uv.lock`.

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
		return frozenset({
			f'extra-{len(pkg_name)}-{pkg_name}-{pymarker_extra}'
			for pymarker_extra in self.pymarker_extras
		})

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

		Notes:
			**Wheels that utilize `platform_release` marker dependencies are incompatible with Blender extensions**.

			This is because there's no way to predict the user's exact `platform_release` when preparing extension wheels.

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
		excl_max_version: tuple[int, int, int] | None = None,
	) -> typ.Self:
		"""Chunk with another `BLVersion`, forming a new `BLVersion` encapsulating both.

		Notes:
			This method chooses to be "optimistic" when it comes to the presumptions that make smooshing a valid operation.

			- **It is strongly suggested to only smoosh `BLVersion`s where these presumptions are guranteed to hold**, ex. by using `self.is_smooshable_with` to filter what to smoosh and what to let be.
			- _It is **strongly recommended** not to smoosh `BLVersion`s with `vendored_site_packages` that differ in any way._

			**Backwards compatibility is presumed** in the following ways:

			- Any code written for the oldest `min_glibc_version` will also work on the largest `min_glibc_version`.
			- Any code written for the oldest `min_macos_version` will also work on the largest `min_macos_version`.
			- Any code written for the oldest `py_sys_version` will also work on the largest `py_sys_version`.
			- Any code relying on the oldest available version of any package in either `vendored_site_packages`, will also work on the newest available version of that package.

			**Capability narrowing** happens in the following ways:

			- The new `released_on` is the largest of the two.
			- The new `valid_manifest_versions` is the smallest common subset.
			- The new `valid_extension_tags` is the smallest common subset.
			- The new `valid_bl_platforms` is the smallest common subset.
			- The new `valid_python_tags` is the smallest common subset.
			- The new `valid_abi_tags` is the smallest common subset.

			**Capability expansion** happens in the following ways:

			- The new `blender_version_min` is the smallest of the two.
			- The new `blender_version_max` is the largest of the two.
			- The new `pymarker_extras` is a union of both.


		Raises:
			ValueError: If the following **unaltered capabilities** differ between `self` and `other`:

				- `pymarker_implementation_name`: It's impossible to smoosh `BLVersion`s that rely on different Python interpreters.
				- `pymarker_platform_python_implementation`: Same reason.

		"""
		if (
			self.pymarker_implementation_name == other.pymarker_implementation_name
			or self.pymarker_platform_python_implementation
			== other.pymarker_platform_python_implementation
		):
			return BLVersion(  # pyright: ignore[reportReturnType]
				released_on=max(self.released_on, other.released_on),
				blender_version_min=min(
					self.blender_version_min, other.blender_version_max
				),
				blender_version_max=max(
					self.blender_version_max,
					other.blender_version_max,
					*([excl_max_version] if excl_max_version is not None else []),
				),
				valid_manifest_versions=(
					self.valid_manifest_versions & other.valid_manifest_versions
				),
				valid_extension_tags=(
					self.valid_extension_tags & other.valid_extension_tags
				),
				valid_bl_platforms=(self.valid_bl_platforms & other.valid_bl_platforms),
				min_glibc_version=min(self.min_glibc_version, other.min_glibc_version),
				min_macos_version=min(self.min_macos_version, other.min_macos_version),
				py_sys_version=min(self.py_sys_version, other.py_sys_version),
				valid_python_tags=(self.valid_python_tags & other.valid_python_tags),
				valid_abi_tags=(self.valid_abi_tags & other.valid_abi_tags),
				pymarker_extras=self.pymarker_extras | other.pymarker_extras,
				pymarker_implementation_name=self.pymarker_implementation_name,
				pymarker_platform_python_implementation=self.pymarker_platform_python_implementation,
				vendored_site_package_strs=frozendict({
					pkg_name: str(
						min([
							*(
								[self.vendored_site_packages[pkg_name]]
								if pkg_name in self.vendored_site_packages
								else []
							),
							*(
								[other.vendored_site_packages[pkg_name]]
								if pkg_name in other.vendored_site_packages
								else []
							),
						])
					)
					for pkg_name in sorted(
						set(self.vendored_site_packages.keys())
						| set(other.vendored_site_packages.keys())
					)
				}),
			)

		msgs = [
			"Can't smoosh two incompatible `BLVersions`.",
			'> **Incompatible Fields** (`self.* != other.*`):',
			f'> - `pymarker_implementation_name`: `{self.pymarker_implementation_name} != {other.pymarker_implementation_name}`',
			f'> - `pymarker_platform_python_implementation`: `{self.pymarker_platform_python_implementation} != {other.pymarker_platform_python_implementation}`',
		]
		raise ValueError(*msgs)

	####################
	# - Sortability
	####################
	def __lt__(self, other: typ.Self) -> bool:
		"""This is less than 'other' when `self.source < other.source`."""
		return (
			*self.blender_version_min,
			self.released_on,
		) < (
			*other.blender_version_min,
			other.released_on,
		)
