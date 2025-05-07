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

"""Implements `BLReleaseOfficial`."""

import datetime as dt
import enum
import functools
import typing as typ

import packaging.version
import pydantic as pyd
from frozendict import frozendict

from .bl_manifest_version import BLManifestVersion
from .bl_platform import BLPlatform
from .bl_version import BLVersion


class BLReleaseOfficial(enum.StrEnum):
	"""Identifier for a supported version of Blender.

	References:
		- Version Compatibility: <https://developer.blender.org/docs/release_notes/compatibility/>
	"""

	# Blender 4.2
	BL4_2_0 = '4.2.0'
	BL4_2_1 = '4.2.1'
	BL4_2_2 = '4.2.2'
	BL4_2_3 = '4.2.3'
	BL4_2_4 = '4.2.4'
	BL4_2_5 = '4.2.5'
	BL4_2_6 = '4.2.6'
	BL4_2_7 = '4.2.7'
	BL4_2_8 = '4.2.8'

	# Blender 4.3
	BL4_3_0 = '4.3.0'
	BL4_3_1 = '4.3.1'
	BL4_3_2 = '4.3.2'

	# Blender 4.4
	BL4_4_0 = '4.4.0'

	####################
	# - Classification
	####################
	@classmethod
	def released_4_2(cls) -> frozenset[typ.Self]:
		"""All released `4.2 LTS` versions of Blender."""
		V = BLReleaseOfficial
		return frozenset(  # pyright: ignore[reportReturnType]
			{
				V.BL4_2_0,
				V.BL4_2_1,
				V.BL4_2_2,
				V.BL4_2_3,
				V.BL4_2_4,
				V.BL4_2_5,
				V.BL4_2_6,
				V.BL4_2_7,
				V.BL4_2_8,
			}
		)

	@classmethod
	def released_4_3(cls) -> frozenset[typ.Self]:
		"""All released `4.3` versions of Blender."""
		V = BLReleaseOfficial
		return frozenset(  # pyright: ignore[reportReturnType]
			{
				V.BL4_3_0,
				V.BL4_3_1,
				V.BL4_3_2,
			}
		)

	@classmethod
	def released_4_4(cls) -> frozenset[typ.Self]:
		"""All released `4.4` versions of Blender."""
		V = BLReleaseOfficial
		return frozenset({V.BL4_4_0})  # pyright: ignore[reportReturnType]

	@classmethod
	def released_4_5(cls) -> frozenset[typ.Self]:
		"""All released `4.5 LTS` versions of Blender."""
		return frozenset()

	@classmethod
	def released_5_0(cls) -> frozenset[typ.Self]:
		"""All released `5.0` versions of Blender."""
		return frozenset()

	####################
	# - Version Check
	####################
	@functools.cached_property
	def is_4_2(self) -> bool:
		"""Whether this version of Blender is a `4.2.*` release."""
		return self in self.released_4_2()

	@functools.cached_property
	def is_4_3(self) -> bool:
		"""Whether this version of Blender is a `4.3.*` release."""
		return self in self.released_4_3()

	@functools.cached_property
	def is_4_4(self) -> bool:
		"""Whether this version of Blender is a `4.4.*` release."""
		return self in self.released_4_4()

	@functools.cached_property
	def is_4_5(self) -> bool:
		"""Whether this version of Blender is a `4.5.*` release."""
		return self in self.released_4_5()

	@functools.cached_property
	def is_5_0(self) -> bool:
		"""Whether this version of Blender is a `5.0.*` release."""
		return self in self.released_5_0()

	####################
	# - Properties
	####################
	@functools.cached_property
	def version(self) -> tuple[int, int, int]:
		"""The official version tuple associated with this release."""
		V = BLReleaseOfficial
		return {
			# Blender 4.2
			V.BL4_2_0: (4, 2, 0),
			V.BL4_2_1: (4, 2, 1),
			V.BL4_2_2: (4, 2, 2),
			V.BL4_2_3: (4, 2, 3),
			V.BL4_2_4: (4, 2, 4),
			V.BL4_2_5: (4, 2, 5),
			V.BL4_2_6: (4, 2, 6),
			V.BL4_2_7: (4, 2, 7),
			V.BL4_2_8: (4, 2, 8),
			# Blender 4.3
			V.BL4_3_0: (4, 3, 0),
			V.BL4_3_1: (4, 3, 1),
			V.BL4_3_2: (4, 3, 2),
			# Blender 4.4
			V.BL4_4_0: (4, 4, 0),
		}[self]

	@functools.cached_property
	def released_on(self) -> dt.datetime:
		"""Date and time that this release was published, as denoted by the `git` tag.

		Notes:
			To retrieve timezone-aware tag creation dates/times from the Blender `git` repository, use:

			```bash
			git for-each-ref --format="%(refname:short) | %(creatordate:iso)" "refs/tags/*"
			```

			Copy-paste each entry here.
		"""
		V = BLReleaseOfficial
		return {
			# Blender 4.2
			V.BL4_2_0: dt.datetime.fromisoformat('2024-07-16 02:20:19 -0400'),
			V.BL4_2_1: dt.datetime.fromisoformat('2024-08-19 13:21:12 +0200'),
			V.BL4_2_2: dt.datetime.fromisoformat('2024-09-23 14:18:24 +0200'),
			V.BL4_2_3: dt.datetime.fromisoformat('2024-10-14 17:20:17 +0200'),
			V.BL4_2_4: dt.datetime.fromisoformat('2024-11-18 11:34:40 +0100'),
			V.BL4_2_5: dt.datetime.fromisoformat('2024-12-16 20:54:56 +0100'),
			V.BL4_2_6: dt.datetime.fromisoformat('2025-01-20 16:04:15 +0100'),
			V.BL4_2_7: dt.datetime.fromisoformat('2025-02-17 13:50:33 +0100'),
			V.BL4_2_8: dt.datetime.fromisoformat('2025-03-17 15:22:41 +0100'),
			# Blender 4.3
			V.BL4_3_0: dt.datetime.fromisoformat('2024-11-19 09:52:10 +0100'),
			V.BL4_3_1: dt.datetime.fromisoformat('2024-12-10 08:46:11 +0100'),
			V.BL4_3_2: dt.datetime.fromisoformat('2024-12-16 22:10:40 +0100'),
			# Blender 4.4
			V.BL4_4_0: dt.datetime.fromisoformat('2025-03-17 18:00:48 +0100'),
		}[self]

	@functools.cached_property
	def official_git_tag(self) -> str:
		"""Name of `git tag` corresponding to this Blender version.

		Notes:
			For all `self.supported_bl_platforms`, this tag is presumed to be valid also for the submodule repositories in `lib/lib-<bl_platform`.
		"""
		return 'v' + '.'.join(str(el) for el in self.version)

	@functools.cached_property
	def min_glibc_version(self) -> tuple[int, int]:
		"""Minimum `glibc` version suported on Linux variants of this Blender version."""
		V = BLReleaseOfficial
		return {
			# Blender 4.2
			V.BL4_2_0: (2, 28),
			V.BL4_2_1: (2, 28),
			V.BL4_2_2: (2, 28),
			V.BL4_2_3: (2, 28),
			V.BL4_2_4: (2, 28),
			V.BL4_2_5: (2, 28),
			V.BL4_2_6: (2, 28),
			V.BL4_2_7: (2, 28),
			V.BL4_2_8: (2, 28),
			# Blender 4.3
			V.BL4_3_0: (2, 28),
			V.BL4_3_1: (2, 28),
			V.BL4_3_2: (2, 28),
			# Blender 4.4
			V.BL4_4_0: (2, 28),
		}[self]

	@functools.cached_property
	def min_macos_version(self) -> tuple[int, int]:
		"""Minimum `macos` version suported on MacOS variants of this Blender version."""
		V = BLReleaseOfficial
		return {
			# Blender 4.2
			## - Follows VFX Reference Platform CY2024, which requires 11.0+ support.
			V.BL4_2_0: (11, 0),
			V.BL4_2_1: (11, 0),
			V.BL4_2_2: (11, 0),
			V.BL4_2_3: (11, 0),
			V.BL4_2_4: (11, 0),
			V.BL4_2_5: (11, 0),
			V.BL4_2_6: (11, 0),
			V.BL4_2_7: (11, 0),
			V.BL4_2_8: (11, 0),
			# Blender 4.3
			V.BL4_3_0: (11, 0),
			V.BL4_3_1: (11, 0),
			V.BL4_3_2: (11, 0),
			# Blender 4.4
			## - Follows VFX Reference Platform CY2025, which requires 12.0+.
			## - Officially, Blender claims to support 11.2+, but we opt for CY2025 minimum.
			## - This is a practical choice - as of 2025-03, 'scipy' needs 12.0+.
			V.BL4_4_0: (12, 0),
		}[self]

	@functools.cached_property
	def valid_manifest_versions(self) -> frozenset[BLManifestVersion]:
		"""Manifest versions supported by this Blender release."""
		M = BLManifestVersion
		match self:
			case v if v.is_4_2 or v.is_4_3 or v.is_4_4 or v.is_4_5:
				return frozenset({M.V1_0_0})
			case _:
				msg = f'Released Blender version `{self}` was not accounted for in `BLReleaseOfficial.valid_manifest_versions`. Please report this bug.'
				raise RuntimeError(msg)

	@functools.cached_property
	def valid_bl_platforms(self) -> frozenset[BLPlatform]:
		"""Officially supported `BLPlatform`s of this Blender version.

		Notes:
			Only platforms with a `lib/` submodule containing tagged Blender versions are included.
			This **may not** correspond to the available [official binary downloads](https://download.blender.org/release/).

			It may be possible to compile Blender manually for wider platform support, but this isn't taken in to account by `blext`.
		"""
		V = BLReleaseOfficial
		P = BLPlatform
		match self:
			case V.BL4_2_0:
				return frozenset({
					P.linux_x64,
					P.macos_x64,
					P.macos_arm64,
					P.windows_x64,
				})
			case v if v.is_4_2:
				return frozenset({
					P.linux_x64,
					P.macos_x64,
					P.macos_arm64,
					P.windows_x64,
					P.windows_arm64,
				})
			case v if v.is_4_3 or v.is_4_4 or v.is_4_5:
				return frozenset({
					P.linux_x64,
					P.macos_x64,
					P.macos_arm64,
					P.windows_x64,
					P.windows_arm64,
				})
			case v if v.is_5_0:
				return frozenset({
					P.linux_x64,
					P.macos_arm64,
					P.windows_x64,
					P.windows_arm64,
				})
			case _:
				msg = f'Released Blender version `{self}` was not accounted for in `BLReleaseOfficial.valid_bl_platforms`. Please report this bug.'
				raise RuntimeError(msg)

	@functools.cached_property
	def valid_extension_tags(self) -> frozenset[str]:
		"""Extension tags parseable by this Blender release."""
		match self:
			case v if v.is_4_2 or v.is_4_3 or v.is_4_4 or v.is_4_5:
				return frozenset({
					'3D View',
					'Add Curve',
					'Add Mesh',
					'Animation',
					'Bake',
					'Camera',
					'Compositing',
					'Development',
					'Game Engine',
					'Geometry Nodes',
					'Grease Pencil',
					'Import-Export',
					'Lighting',
					'Material',
					'Modeling',
					'Mesh',
					'Node',
					'Object',
					'Paint',
					'Pipeline',
					'Physics',
					'Render',
					'Rigging',
					'Scene',
					'Sculpt',
					'Sequencer',
					'System',
					'Text Editor',
					'Tracking',
					'User Interface',
					'UV',
				})
			case _:
				msg = f'Released Blender version `{self}` was not accounted for in `BLReleaseOfficial.valid_extension_tags`. Please report this bug.'
				raise RuntimeError(msg)

	@functools.cached_property
	def vendored_site_packages(self) -> frozendict[str, packaging.version.Version]:
		"""Extension tags parseable by this Blender release."""
		match self:
			case v if v.is_4_2:
				vendored_site_packages = {
					'autopep8': '1.6.0',
					'certifi': '2021.10.8',
					'charset_normalizer': '2.0.10',
					'Cython': '0.29.30',
					'idna': '3.3',
					## MaterialX
					'numpy': '1.24.3',
					## OpenImageIO
					'pip': '23.2.1',
					## pkg_resources
					## pxr
					'pycodestyle': '2.8.0',
					## PyOpenColorIO
					## pyximport
					'requests': '2.27.1',
					'setuptools': '63.2.0',
					'toml': '0.10.2',
					'urllib3': '1.26.8',
					'zstandard': '0.16.0',
					## pyopenvdb
				}
			case v if v.is_4_3:
				vendored_site_packages = {
					'autopep8': '2.3.1',
					'certifi': '2021.10.8',
					'charset_normalizer': '2.0.10',
					'Cython': '0.29.30',
					'idna': '3.3',
					## MaterialX
					'numpy': '1.24.3',
					## OpenImageIO
					'pip': '24.0',
					## pkg_resources
					## pxr
					'pycodestyle': '2.12.1',
					## PyOpenColorIO
					## pyximport
					'requests': '2.27.1',
					'setuptools': '63.2.0',
					'urllib3': '1.26.8',
					'zstandard': '0.16.0',
					## pyopenvdb
				}
			case v if v.is_4_4:
				vendored_site_packages = {
					'autopep8': '2.3.1',
					'certifi': '2021.10.8',
					'charset_normalizer': '2.0.10',
					'Cython': '3.0.11',
					'idna': '3.3',
					## MaterialX
					'numpy': '1.26.4',
					## OpenImageIO
					## oslquery
					'pip': '24.0',
					## pkg_resources
					## pxr
					'pycodestyle': '2.12.1',
					## PyOpenColorIO
					## pyximport
					'requests': '2.27.1',
					'setuptools': '63.2.0',
					'urllib3': '1.26.8',
					'zstandard': '0.16.0',
					## pyopenvdb
				}
			case _:
				msg = f'Released Blender version `{self}` was not accounted for in `BLReleaseOfficial.valid_extension_tags`. Please report this bug.'
				raise RuntimeError(msg)

		# Coerce names to normalized PyPi naming conventions.
		## NOTE: If we don't do this, then conflict detection may spontaneously break.
		return frozendict({
			pkg_name.replace('-', '_').lower(): packaging.version.Version(pkg_version)
			for pkg_name, pkg_version in vendored_site_packages.items()
		})

	####################
	# - Python Environment: Basic Information
	####################
	@functools.cached_property
	def py_sys_version(self) -> tuple[int, int, int, str, int]:
		"""Value of `sys.implementation.version` in this Blender version.

		Notes:
			- On `CPython`, `sys.version_info` is the same as `sys.implementation.version`.
			- The exact (including patch) version of Python shipped with each Blender version is given by-platform, in the submodules of `lib/<bl_platform>`.
			- The exact Python version in use within each platform can be read from `python/include/python3.11/patchlevel.h`.

			In `patchlevel.h`, a block such as the following can be found:
			```
			/* Version parsed out into numeric values */
			/*--start constants--*/
			#define PY_MAJOR_VERSION        3
			#define PY_MINOR_VERSION        11
			#define PY_MICRO_VERSION        11
			#define PY_RELEASE_LEVEL        PY_RELEASE_LEVEL_FINAL
			#define PY_RELEASE_SERIAL       0
			```

			Since Blender only uses `CPython`, this corresponds to both `sys.version_info` and `sys.implementation.version`.

			**Tips**: The `M.m.*` versions often have matching Python versions across platforms and patch-versions. This can be manually validated, one by one, by inserting every supported `<bl_platform>` and `<git_tag>` tag into the following URL:

			```
			https://projects.blender.org/blender/lib-<bl_platform>/src/tag/<git_tag>/python/include/python3.11/patchlevel.h
			```

			**Python Version**: It's presumed that the _exact_ Python version, including patch-versions, is identical across all platforms.
		"""
		match self:
			case v if v.is_4_2:
				return (3, 11, 7, 'final', 0)

			case v if v.is_4_3:
				return (3, 11, 9, 'final', 0)

			case v if v.is_4_4:
				return (3, 11, 11, 'final', 0)

			case _:
				msg = f'Cannot determine Python version of unreleased Blender version: {self.official_git_tag}'
				raise ValueError(msg)

	@functools.cached_property
	def python_version(self) -> str:
		"""`major.minor` version of Python shipped with this Blender version."""
		major, minor, *_ = self.py_sys_version
		return f'{major}.{minor}'

	@functools.cached_property
	def valid_python_tags(self) -> frozenset[str]:
		"""Tags on Python wheels that indicate interpreter compatibility with this Blender version's Python environment."""
		# Base Python Tags
		## The first extension-compatible Blender version has Python 3.11.
		pytags = {
			'py3',
			'cp36',
			'cp37',
			'cp38',
			'cp39',
			'cp310',
			'cp311',
		}

		# Add Python Tags for Higher Python Versions
		## For now, only Python 3.11 ships until at least the VFX Reference Platform CY2026.

		return frozenset(pytags)

	@functools.cached_property
	def valid_abi_tags(self) -> frozenset[str]:
		"""Tags on Python wheels that indicate ABI compatibility with this Blender version's Python environment."""
		# Base ABI Tags
		## The first extension-compatible Blender version has Python 3.11.
		pytags = {
			'none',
			'abi3',
		}

		# Add Python Tags for Higher Python Versions
		## For now, only Python 3.11 ships until at least the VFX Reference Platform CY2026.
		if self.python_version == '3.11':
			pytags.add('cp311')

		return frozenset(pytags)

	####################
	# - Python Environment: Marker Information
	####################
	@functools.cached_property
	def pymarker_extra(self) -> typ.Literal['blender4-2', 'blender4-3', 'blender4-4']:
		"""Optional dependency `extra` name corresponding to this Blender version.

		Notes:
			This is a key to the `[project.optional-dependencies]` table in `pyproject.toml`, which defines Blender version-specific dependencies.

			Blender's bundled `site-packages` must be matched as much as possible, under this property's key, to ensure that `uv`'s resolver finds compatible dependency versions.

			Compared to the keys of `[project.optional-dependencies]` in `pyproject.toml`, this property uses `-` instead of `_`.

			This matches how the `extra` is defined in `uv.lock`.
		"""
		match self:
			case v if v.is_4_2:
				return 'blender4-2'

			case v if v.is_4_3:
				return 'blender4-3'

			case v if v.is_4_4:
				return 'blender4-4'

			case _:
				msg = f'Cannot determine Python version of unreleased Blender version: {self.official_git_tag}'
				raise ValueError(msg)

	@functools.cached_property
	def pymarker_implementation_name(self) -> typ.Literal['cpython']:
		"""Value of `sys.implementation.name` in this Blender version."""
		return 'cpython'

	@functools.cached_property
	def pymarker_platform_python_implementation(self) -> typ.Literal['CPython']:
		"""Value of `sys.implementation.name` in this Blender version."""
		return 'CPython'

	####################
	# - Creation
	####################
	@classmethod
	def from_official_version_range(
		cls, bl_version_min_str: str, bl_version_max_str: str | None = None, /
	) -> frozenset[typ.Self]:
		"""All `ReleasedBLVersion`s within an inclusive/exclusive version range."""
		bl_version_min = tuple(int(el) for el in bl_version_min_str.split('.'))
		bl_version_max = (
			tuple(int(el) for el in bl_version_max_str.split('.'))
			if bl_version_max_str is not None
			else None
		)
		return frozenset(  # pyright: ignore[reportReturnType]
			{
				released_bl_version
				for released_bl_version in BLReleaseOfficial
				if (
					(
						released_bl_version.version[0] == bl_version_min[0]
						and released_bl_version.version[1] == bl_version_min[1]
						and released_bl_version.version[2] >= bl_version_min[2]
					)
					or (
						released_bl_version.version[0] == bl_version_min[0]
						and released_bl_version.version[1] > bl_version_min[1]
					)
					or released_bl_version.version[0] > bl_version_min[0]
				)
				and (
					bl_version_max is None
					or (
						released_bl_version.version[0] == bl_version_max[0]
						and released_bl_version.version[1] == bl_version_max[1]
						and released_bl_version.version[2] < bl_version_max[2]
					)
					or (
						released_bl_version.version[0] == bl_version_max[0]
						and released_bl_version.version[1] < bl_version_max[1]
					)
					or released_bl_version.version[0] < bl_version_max[0]
				)
			}
		)

	####################
	# - Acquisition
	####################
	@functools.cached_property
	def base_download_url(self) -> pyd.HttpUrl:
		"""Base URL from which to search for download URLs for this Blender release."""
		return pyd.HttpUrl('https://download.blender.org/release')

	def download_url_portable(self, bl_platform: BLPlatform) -> pyd.HttpUrl:
		"""URL to a portable variant of this Blender release.

		Notes:
			Availability: Currently, it is not checked whether `bl_platform` has an official Blender download available.

			Always check that this URL exists and looks reasonable before downloading anything.
		"""
		version_major_minor = '.'.join(str(v) for v in self.version[:2])
		return pyd.HttpUrl(
			'/'.join([
				str(self.base_download_url),
				f'Blender{version_major_minor}',
				f'blender-{version_major_minor}-{bl_platform}.{bl_platform.official_archive_file_ext}',
			])
		)

	####################
	# - Transformation
	####################
	@functools.cached_property
	def bl_version(self) -> BLVersion:
		"""The Blender version corresponding to this release."""
		return BLVersion(
			released_on=self.released_on,
			blender_version_min=self.version,
			blender_version_max=self.version[:2] + (self.version[2] + 1,),
			valid_manifest_versions=self.valid_manifest_versions,
			valid_extension_tags=self.valid_extension_tags,
			valid_bl_platforms=self.valid_bl_platforms,
			min_glibc_version_tuple=self.min_glibc_version,
			min_macos_version_tuple=self.min_macos_version,
			py_sys_version=self.py_sys_version,
			valid_python_tags=self.valid_python_tags,
			valid_abi_tags=self.valid_abi_tags,
			pymarker_extras=frozenset({self.pymarker_extra}),
			pymarker_implementation_name=self.pymarker_implementation_name,
			pymarker_platform_python_implementation=self.pymarker_platform_python_implementation,
			vendored_site_package_strs=frozendict({
				pkg_name: str(pkg_version)
				for pkg_name, pkg_version in self.vendored_site_packages.items()
			}),
		)
