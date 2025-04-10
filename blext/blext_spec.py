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

"""Defines the Blender extension specification."""

import functools
import tomllib
import typing as typ
from pathlib import Path

import annotated_types as atyp
import pydantic as pyd
from frozendict import frozendict
from pydantic_extra_types.semantic_version import SemanticVersion

from . import extyp
from .pydeps import BLExtDeps, PyDepWheel, uv
from .utils.inline_script_metadata import parse_inline_script_metadata
from .utils.lru_method import lru_method
from .utils.pydantic_frozendict import FrozenDict


####################
# - Blender Extension Specification
####################
class BLExtSpec(pyd.BaseModel, frozen=True):
	"""Specifies a Blender extension.

	This model allows `pyproject.toml` to be the single source of truth for a Blender extension project.
	Thus, this model is designed to be parsed entirely from a `pyproject.toml` file, and in turn is capable of generating the Blender extension manifest file and more.

	To the extent possible, appropriate standard `pyproject.toml` fields are scraped for information relevant to a Blender extension. | None = None
	This includes name, version, license, desired dependencies, homepage, and more.
	Naturally, many fields are _quite_ specific to Blender extensions, such as Blender version constraints, permissions, and extension tags.
	For such options, the `[tool.blext]` section is introduced.

	Attributes:
		wheels_graph: All wheels that might be usable by this extension.
		release_profile: Optional initialization settings and spec overrides.
			**Overrides must be applied during construction**.
		id: Unique identifying name of the extension.
		name: Pretty, user-facing name of the extension.
		version: The version of the extension.
		tagline: Short description of the extension.
		maintainer: Primary maintainer of the extension (name and email).
		type: Type of extension.
			Currently, only `add-on` is supported.
		blender_version_min: The minimum version of Blender that this extension supports.
		blender_version_max: The maximum version of Blender that this extension supports.
		wheels: Relative paths to wheels distributed with this extension.
			These should be installed by Blender alongside the extension.
			See <https://docs.blender.org/manual/en/dev/extensions/python_wheels.html> for more information.
		permissions: Permissions required by the extension.
		tags: Tags for categorizing the extension.
		license: License of the extension's source code.
		copyright: Copyright declaration of the extension.
		website: Homepage of the extension.

	References:
		- <https://docs.blender.org/manual/en/4.2/extensions/getting_started.html>
		- <https://packaging.python.org/en/latest/guides/writing-pyproject-toml>
	"""

	granular_bl_platforms: typ.Annotated[frozenset[extyp.BLPlatform], atyp.MinLen(1)]
	deps: BLExtDeps
	release_profile: extyp.ReleaseProfile | None = None

	id: typ.Annotated[
		str,
		atyp.Predicate(str.isidentifier),
		atyp.Predicate(extyp.validators.no_dunder_in_string),
		atyp.Predicate(extyp.validators.no_str_startswith_underscore),
		atyp.Predicate(extyp.validators.no_str_endswith_underscore),
	]
	name: typ.Annotated[
		str,
		atyp.Predicate(extyp.validators.is_str_strip_not_empty),
		atyp.Predicate(extyp.validators.is_str_strip_a_noop),
		atyp.Predicate(extyp.validators.str_has_no_bl_control_chars),
	]
	tagline: typ.Annotated[
		str,
		atyp.MaxLen(64),
		atyp.Predicate(extyp.validators.no_dunder_in_string),
		atyp.Predicate(extyp.validators.no_str_startswith_underscore),
		atyp.Predicate(extyp.validators.no_str_endswith_underscore),
		atyp.Predicate(extyp.validators.last_char_is_alphanum_or_closes_bracket),
	]
	version: SemanticVersion
	license: extyp.SPDXLicense
	blender_version_min: typ.Annotated[
		str,
		atyp.Predicate(extyp.validators.all_version_numbers_are_digits),
		atyp.Predicate(extyp.validators.blender_version_is_gt_4_2),
	]
	blender_version_max: (
		typ.Annotated[
			str,
			atyp.Predicate(extyp.validators.all_version_numbers_are_digits),
			atyp.Predicate(extyp.validators.blender_version_is_gt_4_2),
		]
		| None
	) = None
	permissions: (
		FrozenDict[
			typ.Literal['files', 'network', 'clipboard', 'camera', 'microphone'],
			typ.Annotated[
				str,
				atyp.MaxLen(64),
				atyp.Predicate(extyp.validators.no_dunder_in_string),
				atyp.Predicate(extyp.validators.no_str_startswith_underscore),
				atyp.Predicate(extyp.validators.no_str_endswith_underscore),
				atyp.Predicate(
					extyp.validators.last_char_is_alphanum_or_closes_bracket
				),
			],
		]
		| None
	) = None
	copyright: (
		tuple[
			typ.Annotated[
				str,
				atyp.Predicate(extyp.validators.is_copyright_year_valid),
				atyp.Predicate(extyp.validators.is_copyright_name_valid),
			],
			...,
		]
		| None
	) = None
	maintainer: (
		typ.Annotated[
			str,
			atyp.Predicate(extyp.validators.is_str_strip_not_empty),
			atyp.Predicate(extyp.validators.is_str_strip_a_noop),
			atyp.Predicate(extyp.validators.str_has_no_bl_control_chars),
		]
		| None
	) = None
	tags: frozenset[str] | None = None
	website: pyd.HttpUrl | None = None

	####################
	# - Blender Versions
	####################
	@functools.cached_property
	def granular_bl_versions(self) -> frozenset[extyp.BLVersion]:
		"""Exhaustive, unsmooshed Blender versions supported by this extension.

		Notes:
			Granular `BLVersion`s include each and every explicit ex. `4.2.1`, `4.2.2`.
			By contrast, `self.bl_versions` provides "smooshed" versions ex. `4.2.0-4.3.0`

			Derived from `self.blender_version_(min|max)`, using `extyp.BLReleaseOfficial.from_official_version_range`.
		"""
		return frozenset({
			released_bl_version.bl_version
			for released_bl_version in extyp.BLReleaseOfficial.from_official_version_range(
				self.blender_version_min, self.blender_version_max
			)
		})

	@functools.cached_property
	def sorted_granular_bl_versions(self) -> tuple[extyp.BLVersion, ...]:
		"""Sorted variant of `self.granular_bl_versions`.

		Notes:
			The sorting order first prioritizes `blender_version_min` first, then prioritizes the release datetime.

			Intuitively, though not formally, this should ensure a consistent, sensible ordering for any constellation of `BLVersion`s.
		"""
		return tuple(sorted(self.granular_bl_versions))

	@functools.cached_property
	def bl_versions_by_granular(self) -> frozendict[extyp.BLVersion, extyp.BLVersion]:
		"""Map from supported _granular_ `BLVersion`s to supported _smooshed_ `BLVersion`s.

		Notes:
			**The output `frozendict` is guaranteed to be created in the same order as `self.sorted_granular_bl_versions`**.

			Each granular `BLVersion` from `self.granular_bl_version` is guaranteed to be included in one of the the corresponding "smooshed" `BLVersion`s in `self.bl_versions`.

			This method provides that mapping.
		"""
		# Initialize Consecutive "Smooshing"
		## Non-consecutive Blender versions are extremely unlikely to be "smooshable".
		## We define "consecutive" using the ordering of 'self.sorted_granular_bl_versions'.
		idx_smoosh = 0
		smooshed_bl_versions: list[extyp.BLVersion] = [
			self.sorted_granular_bl_versions[0]
		]
		granular_to_smooshed_idx: dict[extyp.BLVersion, int] = {
			self.sorted_granular_bl_versions[0]: 0
		}

		# Traverse Consecutive Versions for Potential "Smooshing"
		## Think building an injective map of pointers from granular to partially smooshed.
		## If / when a version is reached that can't be "smooshed into" previous, increment.
		## => If only consecutive BLVersions are smooshable, this should min. # of outputs.
		for granular_bl_version in self.sorted_granular_bl_versions[1:]:
			if smooshed_bl_versions[idx_smoosh].is_smooshable_with(
				granular_bl_version,
				ext_bl_platforms=self.granular_bl_platforms,
				ext_wheels_python_tags=self.deps.valid_python_tags,
				ext_wheels_abi_tags=self.deps.valid_abi_tags,
				ext_tags=self.tags,
			):
				smooshed_bl_versions[idx_smoosh] = smooshed_bl_versions[
					idx_smoosh
				].smoosh_with(
					granular_bl_version,
					excl_max_version=tuple(  # pyright: ignore[reportArgumentType]
						int(v) for v in self.blender_version_max.split('.')
					)
					if self.blender_version_max is not None
					else None,
				)

			else:
				smooshed_bl_versions.append(granular_bl_version)
				idx_smoosh += 1

			granular_to_smooshed_idx[granular_bl_version] = idx_smoosh

		# Return Constructed Mapping
		## We recorded pointers from granular to the smooshed version it's included in.
		## By following those pointers, we're left only with the desired mapping.
		return frozendict({
			granular_bl_version: smooshed_bl_versions[smooshed_idx]
			for granular_bl_version, smooshed_idx in granular_to_smooshed_idx.items()
		})

	@functools.cached_property
	def bl_versions(self) -> frozenset[extyp.BLVersion]:
		"""All Blender versions supported by this extension.

		Notes:
			`blext` doesn't support official Blender versions released after a particular `blext` version was published.

			This is because `blext` has no way of knowing critical information about such future releases, ex. the versions of vendored `site-packages` dependencies.

			Derived by comparing `self.blender_version_min` and `self.blender_version_max` to hard-coded Blender versions that have already been released, whose properties are known.
		"""
		return frozenset(self.bl_versions_by_granular.values())

	@functools.cached_property
	def sorted_bl_versions(self) -> tuple[extyp.BLVersion, ...]:
		"""Sorted variant of `self.bl_versions`.

		Notes:
			**`self.bl_versions_by_granular` must be sorted in the same order as `self.sorted_granular_bl_versions`**.
		"""
		# NOTE: This is an order-preserving deduplication.
		## `dict` performs insertion-order preserving deduplication of the `.values()`.
		## The keys of this temporary `dict` are then dumped into a new tuple w/unpacking.
		return (*dict.fromkeys(self.bl_versions_by_granular.values()),)

	####################
	# - Blender Platforms
	####################
	@functools.cached_property
	def is_platform_universal(self) -> bool:
		"""Whether this extension is works on all platforms of all supported Blender versions.

		Notes:
			Pure-Python extensions that only use pure-Python dependencies are considered "universal".

			Once any non-pure-Python wheels are introduced, this condition may become very difficult to uphold, depending on which wheels are available for supported platforms.
		"""
		return all(
			bl_version.valid_bl_platforms.issubset(self.granular_bl_platforms)
			for bl_version in self.bl_versions
		)

	@functools.cached_property
	def sorted_granular_bl_platforms(self) -> tuple[extyp.BLPlatform, ...]:
		"""Sorted variant of `self.bl_platforms`."""
		return tuple(sorted(self.granular_bl_platforms))

	@functools.cached_property
	def bl_platforms_by_granular(
		self,
	) -> frozendict[extyp.BLPlatform, extyp.BLPlatforms]:
		"""Map from supported _granular_ `BLPlatform`s to supported _smooshed_ `BLPlatform`s."""
		# Initialize Consecutive "Smooshing"
		## Non-consecutive Blender versions are extremely unlikely to be "smooshable".
		## We define "consecutive" using the ordering of 'self.sorted_granular_bl_versions'.
		idx_smoosh = 0
		smooshed_bl_platforms: list[extyp.BLPlatforms] = [
			extyp.BLPlatforms.from_bl_platform(self.sorted_granular_bl_platforms[0])
		]
		granular_to_smooshed_idx: dict[extyp.BLPlatform, int] = {
			self.sorted_granular_bl_platforms[0]: 0
		}

		# Traverse Consecutive Versions for Potential "Smooshing"
		## Think building an injective map of pointers from granular to partially smooshed.
		## If / when a version is reached that can't be "smooshed into" previous, increment.
		## => If only consecutive BLVersions are smooshable, this should min. # of outputs.
		for granular_bl_platform in self.sorted_granular_bl_platforms[1:]:
			if smooshed_bl_platforms[idx_smoosh].is_smooshable_with(
				granular_bl_platform,
				ext_bl_versions=self.bl_versions,
				ext_min_glibc_version=self.deps.min_glibc_version,
				ext_min_macos_version=self.deps.min_macos_version,
				ext_wheels_granular=self.wheels_granular,
			):
				smooshed_bl_platforms[idx_smoosh] = smooshed_bl_platforms[
					idx_smoosh
				].smoosh_with(granular_bl_platform)

			else:
				smooshed_bl_platforms.append(
					extyp.BLPlatforms.from_bl_platform(granular_bl_platform)
				)
				idx_smoosh += 1

			granular_to_smooshed_idx[granular_bl_platform] = idx_smoosh

			# Return Constructed Mapping
			## We recorded pointers from granular to the smooshed version it's included in.
			## By following those pointers, we're left only with the desired mapping.
		return frozendict({
			granular_bl_platform: smooshed_bl_platforms[smooshed_idx]
			for granular_bl_platform, smooshed_idx in granular_to_smooshed_idx.items()
		})

	@functools.cached_property
	def sorted_bl_platforms(self) -> tuple[extyp.BLPlatforms, ...]:
		"""Sorted variant of `self.bl_platforms`."""
		# NOTE: This is an order-preserving deduplication.
		## `dict` performs insertion-order preserving deduplication of the `.values()`.
		## The keys of this temporary `dict` are then dumped into a new tuple w/unpacking.
		return (*dict.fromkeys(self.bl_platforms_by_granular.values()),)

	@functools.cached_property
	def bl_platforms(self) -> frozenset[extyp.BLPlatforms]:
		"""Sorted variant of `self.bl_platforms`."""
		return frozenset(self.bl_platforms_by_granular.values())

	####################
	# - Wheels
	####################
	@functools.cached_property
	def wheels_granular(
		self,
	) -> frozendict[
		extyp.BLVersion, frozendict[extyp.BLPlatform, frozenset[PyDepWheel]]
	]:
		"""All Python wheels needed by the extension, by version and granlar platform."""
		# Initialize Error Aggregators
		## These will collect errors in finding wheels across each version and platform.
		err_msgs = {
			bl_version: {
				bl_platform: list[str]()
				for bl_platform in self.sorted_granular_bl_platforms
				if bl_platform in bl_version.valid_bl_platforms
			}
			for bl_version in self.sorted_bl_versions
		}
		err_num_missing_wheels = {
			bl_version: dict.fromkeys(self.sorted_granular_bl_platforms, 0)
			for bl_version in self.sorted_bl_versions
		}

		# Collect Wheels by version snd platform.
		wheels_granular = frozendict[
			extyp.BLVersion, frozendict[extyp.BLPlatform, frozenset[PyDepWheel]]
		]({
			bl_version: frozendict[extyp.BLPlatform, frozenset[PyDepWheel]]({
				bl_platform: self.deps.wheels_by(
					pkg_name=self.id,
					bl_version=bl_version,
					bl_platform=bl_platform,
					err_msgs=err_msgs,
					err_num_missing_wheels=err_num_missing_wheels,
				)
				for bl_platform in self.granular_bl_platforms
				if bl_platform in bl_version.valid_bl_platforms
			})
			for bl_version in self.sorted_bl_versions
		})

		total_missing_wheels = sum(
			missing_wheels
			for missing_by_platform in err_num_missing_wheels.values()
			for missing_wheels in missing_by_platform.values()
		)
		if total_missing_wheels == 0:
			return wheels_granular

		msgs = [
			err_msg
			for bl_platform_err_msgs in err_msgs.values()
			for err_msg in bl_platform_err_msgs
		] + [
			f'**Missing Wheels** for `{bl_version.pretty_version}`:\n'
			+ '\n'.join([
				f'> `{bl_platform}`: {err_num_missing_wheels[bl_version][bl_platform]}'
				for bl_platform in self.sorted_granular_bl_platforms
				if bl_platform in bl_version.valid_bl_platforms
			])
			for bl_version in self.sorted_bl_versions
		]
		raise ValueError(*msgs)

	@functools.cached_property
	def wheels(
		self,
	) -> frozendict[
		extyp.BLVersion, frozendict[extyp.BLPlatforms, frozenset[PyDepWheel]]
	]:
		"""All Python wheels needed by the extension, by version and platform."""
		return frozendict({
			bl_version: frozendict[extyp.BLPlatforms, frozenset[PyDepWheel]]({
				bl_platform: functools.reduce(
					lambda a, b: a | b,
					(
						self.wheels_granular[bl_version][granular_bl_platform]
						for granular_bl_platform in bl_platform.bl_platforms
						if granular_bl_platform in bl_version.valid_bl_platforms
					),
				)
				for bl_platform in self.sorted_bl_platforms
			})
			for bl_version in self.sorted_bl_versions
		})

	@functools.cached_property
	def wheels_by_bl_version(
		self,
	) -> frozendict[extyp.BLVersion, frozenset[PyDepWheel]]:
		"""All Python wheels needed by the extension, by version alone."""
		return frozendict({
			bl_version: functools.reduce(
				lambda a, b: a | b,
				self.wheels[bl_version].values(),
			)
			for bl_version in self.sorted_bl_versions
		})

	@functools.cached_property
	def bl_versions_by_wheel(
		self,
	) -> frozendict[PyDepWheel, frozenset[extyp.BLVersion]]:
		"""All Blender versions requesting each particular wheel."""
		all_wheels = {
			wheel for wheels in self.wheels_by_bl_version.values() for wheel in wheels
		}
		return frozendict({
			wheel: frozenset({
				bl_version
				for bl_version in self.sorted_bl_versions
				if wheel in self.wheels_by_bl_version[bl_version]
			})
			for wheel in all_wheels
		})

	####################
	# - Attributes
	####################
	@functools.cached_property
	def sorted_tags(self) -> tuple[str, ...] | None:
		"""Alphabetically sorted variant of `self.tags`."""
		return tuple(sorted(self.tags)) if self.tags is not None else None

	####################
	# - Extension Manifest
	####################
	@lru_method()
	def bl_manifests(
		self,
		bl_manifest_version: extyp.BLManifestVersion,
	) -> frozendict[extyp.BLVersion, frozendict[extyp.BLPlatforms, extyp.BLManifest]]:
		"""Export the Blender extension manifest.

		Notes:
			Only `fmt='toml'` results in valid contents of `blender_manifest.toml`.
			_This is also the default._

			Other formats are included to enable easier interoperability with other systems - **not** with Blender.

		Parameters:
			bl_manifest_version: The Blender manifest schema version to export to the appropriate filename.

		Returns:
			String representing the Blender extension manifest.

		Raises:
			ValueError: When `fmt` is unknown.
		"""
		match bl_manifest_version:
			case extyp.BLManifestVersion.V1_0_0:
				return frozendict({
					bl_version: frozendict[extyp.BLPlatforms, extyp.BLManifest_1_0_0]({
						bl_platform: extyp.BLManifest_1_0_0(
							id=self.id,
							name=self.name,
							version=str(self.version),
							tagline=self.tagline,
							maintainer=self.maintainer,
							blender_version_min='.'.join(
								str(v) for v in bl_version.blender_version_min
							),
							blender_version_max='.'.join(
								str(v) for v in bl_version.blender_version_max
							),
							permissions=self.permissions,
							platforms=bl_platform.sorted_bl_platforms,  # pyright: ignore[reportArgumentType]
							tags=self.sorted_tags,
							license=(self.license,),
							copyright=self.copyright,
							website=str(self.website)
							if self.website is not None
							else None,
							wheels=tuple(
								sorted([
									f'./wheels/{wheel.filename}'
									for wheel in self.wheels[bl_version][bl_platform]
								])
							)
							if len(self.wheels[bl_version]) > 0
							else None,
						)
						for bl_platform in self.sorted_bl_platforms
					})
					for bl_version in self.sorted_bl_versions
				})

	@lru_method()
	def bl_manifest_strs(
		self,
		bl_manifest_version: extyp.BLManifestVersion,
		*,
		fmt: typ.Literal['json', 'toml'],
	) -> frozendict[extyp.BLVersion, frozendict[extyp.BLPlatforms, str]]:
		"""Export the Blender extension manifest.

		Notes:
			Only `fmt='toml'` results in valid contents of `blender_manifest.toml`.
			_This is also the default._

			Other formats are included to enable easier interoperability with other systems - **not** with Blender.

		Parameters:
			fmt: String format to export Blender manifest to.

		Returns:
			String representing the Blender extension manifest.

		Raises:
			ValueError: When `fmt` is unknown.
		"""
		bl_manifests = self.bl_manifests(bl_manifest_version)
		return frozendict({
			bl_version: frozendict[extyp.BLPlatforms, extyp.BLManifest]({
				bl_platform: bl_manifests[bl_version][bl_platform].export(fmt=fmt)
				for bl_platform in self.sorted_bl_platforms
			})
			for bl_version in self.sorted_bl_versions
		})

	####################
	# - Extension Filename/Path
	####################
	@functools.cached_property
	def extension_filenames(
		self,
	) -> frozendict[extyp.BLVersion, frozendict[extyp.BLPlatforms, str]]:
		"""Filename of each extension filename to build from this spec."""
		return frozendict({
			bl_version: frozendict[extyp.BLPlatforms, str]({
				bl_platform: (
					f'{self.id}-{str(self.version).replace(".", "_")}__{bl_version.pretty_version.replace(".", "_")}__{bl_platform}'
					if not self.is_platform_universal
					else f'{self.id}_{str(self.version).replace(".", "_")}__{bl_version.pretty_version.replace(".", "_")}'
				)
				for bl_platform in self.sorted_bl_platforms
			})
			for bl_version in self.sorted_bl_versions
		})

	def extension_zip_paths(
		self, *, path_base: Path
	) -> frozendict[extyp.BLVersion, frozendict[extyp.BLPlatforms, Path]]:
		"""Paths to each extension to build from this spec, relative to `path_base`."""
		return frozendict({
			bl_version: frozendict[extyp.BLPlatforms, Path]({
				bl_platform: (
					path_base
					/ (self.extension_filenames[bl_version][bl_platform] + '.zip')
				)
				for bl_platform in self.sorted_bl_platforms
			})
			for bl_version in self.sorted_bl_versions
		})

	####################
	# - Queries: Wheels
	####################
	@lru_method()
	def query_required_wheels(
		self,
		*,
		bl_versions: frozenset[extyp.BLVersion] | None = None,
		bl_platforms: frozenset[extyp.BLPlatforms] | None = None,
	) -> frozenset[PyDepWheel]:
		"""All wheels that are needed to build extensions for all `bl_versions`.

		Parameters:
			bl_versions: Blender versions to find all wheels for.

				- When `None`, use `self.bl_versions`.

		Returns:
			The union-set of wheels needed by all given `bl_versions`, together.
		"""
		# Check Validity of BLVersions
		bl_versions = self.bl_versions if bl_versions is None else bl_versions
		if not all(bl_version in self.bl_versions for bl_version in bl_versions):
			msg = 'Requested all required wheels for `bl_versions`, but one was not also given in `self.bl_versions`.'
			raise ValueError(msg)

		# Check Validity of BLPlatforms
		bl_platforms = self.bl_platforms if bl_platforms is None else bl_platforms
		if not all(bl_platform in self.bl_platforms for bl_platform in bl_platforms):
			msg = 'Requested all required wheels for `bl_platforms`, but one was not also given in `self.bl_platforms`.'
			raise ValueError(msg)

		return frozenset({
			wheel
			for bl_version in bl_versions
			for bl_platform in bl_platforms
			for wheel in self.wheels[bl_version][bl_platform]
		})

	@lru_method()
	def query_cached_wheels(
		self,
		*,
		path_wheels: Path,
		bl_versions: frozenset[extyp.BLVersion] | None = None,
		bl_platforms: frozenset[extyp.BLPlatforms] | None = None,
	) -> frozenset[PyDepWheel]:
		"""Wheels that have already been correctly downloaded."""
		return frozenset({
			wheel
			for wheel in self.query_required_wheels(
				bl_versions=bl_versions, bl_platforms=bl_platforms
			)
			if wheel.is_download_valid(path_wheels / wheel.filename)
		})

	@lru_method()
	def query_missing_wheels(
		self,
		*,
		path_wheels: Path,
		bl_versions: frozenset[extyp.BLVersion] | None = None,
		bl_platforms: frozenset[extyp.BLPlatforms] | None = None,
	) -> frozenset[PyDepWheel]:
		"""Wheels that need to be downloaded, since they are not available / valid."""
		return frozenset({
			wheel
			for wheel in self.query_required_wheels(
				bl_versions=bl_versions, bl_platforms=bl_platforms
			)
			if not wheel.is_download_valid(path_wheels / wheel.filename)
		})

	####################
	# - Queries: Prepack
	####################
	@lru_method()
	def wheel_paths_to_prepack(
		self, *, path_wheels: Path
	) -> frozendict[
		extyp.BLVersion, frozendict[extyp.BLPlatforms, frozendict[Path, Path]]
	]:
		"""Wheel file paths that should be pre-packed."""
		return frozendict({
			bl_version: frozendict[extyp.BLPlatforms, frozendict[Path, Path]]({
				bl_platform: frozendict[Path, Path]({
					path_wheels / wheel.filename: Path('wheels') / wheel.filename
					for wheel in self.wheels[bl_version][bl_platform]
				})
				for bl_platform in self.sorted_bl_platforms
			})
			for bl_version in self.sorted_bl_versions
		})

	####################
	# - Creation
	####################
	@classmethod
	def from_proj_spec_dict(  # noqa: C901, PLR0912, PLR0915
		cls,
		proj_spec_dict: dict[str, typ.Any],
		*,
		path_uv_exe: Path,
		path_proj_spec: Path,
		release_profile_id: extyp.StandardReleaseProfile | str | None,
	) -> typ.Self:
		"""Parse an extension spec from a dictionary.

		Notes:
			- The dictionary is presumed to be loaded directly from either a `pyproject.toml` file or inline script metadata.
			Therefore, please refer to the `pyproject.toml` documentation for more on the dictionary's structure.

			- This method aims to "show its work", in explaining exactly why parsing fails.
			To provide pleasant user feedback, print `ValueError` arguments as Markdown.

		Parameters:
			proj_spec_dict: Dictionary representation of a `pyproject.toml` or inline script metadata.
			path_proj_spec: Path to the file that defines the extension project.
			release_profile_id: Identifier to deduce release profile settings with.
			path_uv_exe: Optional overriden path to a `uv` executable.
				_Generally sourced from `blext.ui.GlobalConfig.path_uv_exe`_.

		Raises:
			ValueError: If the dictionary cannot be parsed to a complete `BLExtSpec`.
				_Messages are valid Markdown_.

		"""
		is_proj_metadata = path_proj_spec.name == 'pyproject.toml'
		is_script_metadata = path_proj_spec.name.endswith('.py')

		####################
		# - Parsing: Stage 1
		####################
		###: Determine whether all required fields are accessible.

		# [project]
		if proj_spec_dict.get('project') is not None:
			project: dict[str, typ.Any] = proj_spec_dict['project']
		else:
			msgs = [
				f'**Invalid Extension Specification**: `{path_proj_spec}` exists, but has no `[project]` table.',
			]
			raise ValueError(*msgs)

		# [tool.blext]
		if (
			proj_spec_dict.get('tool') is not None
			and proj_spec_dict['tool'].get('blext') is not None  # pyright: ignore[reportAny]
			and isinstance(proj_spec_dict['tool']['blext'], dict)
		):
			blext_spec_dict: dict[str, typ.Any] = proj_spec_dict['tool']['blext']
		else:
			msgs = [
				'**Invalid Extension Specification**: No `[tool.blext]` table found.',
				f'> **Spec Path**: `{path_proj_spec}`',
				'>',
				'> **Suggestions**',
				'> - Is this project an extension?',
				'> - Add the `[tool.blext]` table. See the documentation for more.',
			]
			raise ValueError(*msgs)

		# [tool.blext.profiles]
		release_profile: None | extyp.ReleaseProfile = None
		if blext_spec_dict.get('profiles') is not None:
			project_release_profiles: dict[str, typ.Any] = blext_spec_dict['profiles']
			if release_profile_id in project_release_profiles:
				release_profile = extyp.ReleaseProfile(
					**project_release_profiles[release_profile_id]  # pyright: ignore[reportAny]
				)

		if release_profile is None and isinstance(
			release_profile_id, extyp.StandardReleaseProfile
		):
			release_profile = release_profile_id.release_profile

		elif release_profile_id is None:
			release_profile = None

		else:
			msgs = [
				'**Invalid Extension Specification**:',
				f'|    The selected "release profile" `{release_profile_id}` is not a standard release profile...',
				"|    ...and wasn't found in `[tool.blext.profiles]`.",
				'|',
				f'|    Please either define `{release_profile_id}` in `[tool.blext.profiles]`, or select a standard release profile.',
				'|',
				f'**Standard Release Profiles**: `{", ".join(extyp.StandardReleaseProfile)}`',
			]
			raise ValueError(*msgs)

		####################
		# - Parsing: Stage 2
		####################
		###: Parse values that require transformations.

		field_parse_errs: list[str] = []

		# project.requires-python
		project_requires_python: str | None = None
		if (is_proj_metadata and project.get('requires-python') is not None) or (
			is_script_metadata and proj_spec_dict.get('requires-python') is not None
		):
			if is_proj_metadata:
				requires_python_field = project['requires-python']  # pyright: ignore[reportAny]
			elif is_script_metadata:
				requires_python_field = proj_spec_dict['requires-python']  # pyright: ignore[reportAny]
			else:
				msg = 'BLExtSpec metadata is neither project nor script metadata. Something is very wrong.'
				raise RuntimeError(msg)

			if isinstance(requires_python_field, str):
				project_requires_python = requires_python_field.replace('~= ', '')
			else:
				field_parse_errs.append(
					f'- `project.requires-python` must be a string (current value: {project["requires-python"]})'
				)
		else:
			field_parse_errs.append('- `project.requires-python` is not defined.')

		# project.maintainers
		first_maintainer: dict[str, str] | None = None
		if project.get('maintainers') is not None:
			if isinstance(project['maintainers'], list):
				maintainers: list[typ.Any] = project['maintainers']
				if len(maintainers) > 0 and all(
					isinstance(maintainer, dict)
					and 'name' in maintainer
					and isinstance(maintainer['name'], str)
					and 'email' in maintainer
					and isinstance(maintainer['email'], str)
					for maintainer in maintainers  # pyright: ignore[reportAny]
				):
					first_maintainer = maintainers[0]
				else:
					field_parse_errs.append(
						f'- `project.maintainers` is malformed. It must be a **non-empty** list of dictionaries, where each dictionary has a "name: str" and an "email: str" field (current value: {maintainers}).'
					)
			else:
				field_parse_errs.append(
					f'- `project.maintainers` must be a list (current value: {project["maintainers"]})'
				)
		else:
			first_maintainer = {'name': 'Unknown', 'email': 'unknown@example.com'}

		# project.license
		extension_license: str | None = None
		if project.get('license') is not None and isinstance(project['license'], str):
			extension_license = project['license']
		else:
			field_parse_errs.append(
				'- `project.license` is not defined, or is not a string.'
			)
			field_parse_errs.append(
				'- Please note that all Blender addons MUST declare a GPL-compatible license: <https://docs.blender.org/manual/en/latest/advanced/extensions/licenses.html>'
			)

		## project.urls.homepage
		if (
			project.get('urls') is not None
			and isinstance(project['urls'], dict)
			and project['urls'].get('Homepage') is not None  # pyright: ignore[reportUnknownMemberType]
			and isinstance(project['urls']['Homepage'], str)
		):
			homepage = project['urls']['Homepage']
		else:
			homepage = None

		####################
		# - Parsing: Stage 3
		####################
		###: Parse field availability and provide for descriptive errors
		if project.get('name') is None:
			field_parse_errs += ['- `project.name` is not defined.']
		if blext_spec_dict.get('pretty_name') is None:
			field_parse_errs += ['- `tool.blext.pretty_name` is not defined.']
		if project.get('version') is None:
			field_parse_errs += ['- `project.version` is not defined.']
		if project.get('description') is None:
			field_parse_errs += ['- `project.description` is not defined.']
		if blext_spec_dict.get('blender_version_min') is None:
			field_parse_errs += ['- `tool.blext.blender_version_min` is not defined.']
		if blext_spec_dict.get('blender_version_max') is None:
			field_parse_errs += ['- `tool.blext.blender_version_max` is not defined.']
		if blext_spec_dict.get('copyright') is None:
			field_parse_errs += ['- `tool.blext.copyright` is not defined.']
			field_parse_errs += [
				'- Example: `copyright = ["<current_year> <proj_name> Contributors`'
			]

		if field_parse_errs:
			msgs = [
				f'In `{path_proj_spec}`:',
				*field_parse_errs,
			]
			raise ValueError(*msgs)

		####################
		# - Parsing: Stage 4
		####################
		###: Let pydantic take over the last stage of parsing.

		if project_requires_python is None or extension_license is None:
			msg = 'While parsing the project specification, some variables attained a theoretically impossible value. This is a serious bug, please report it!'
			raise RuntimeError(msg)

		# Compute Path to uv.lock
		if path_proj_spec.name == 'pyproject.toml':
			path_uv_lock = path_proj_spec.parent / 'uv.lock'
		elif path_proj_spec.name.endswith('.py'):
			path_uv_lock = path_proj_spec.parent / (path_proj_spec.name + '.lock')
		else:
			msg = f'Invalid project specification path: {path_proj_spec}. Please report this error as a bug.'
			raise RuntimeError(msg)

		_spec_params = {
			'granular_bl_platforms': blext_spec_dict.get('supported_platforms'),
			'deps': BLExtDeps.from_uv_lock(
				uv.parse_uv_lock(
					path_uv_lock,
					path_uv_exe=path_uv_exe,
				),
				module_name=project['name'],  # pyright: ignore[reportAny]
				min_glibc_version=blext_spec_dict.get('min_glibc_version'),
				min_macos_version=blext_spec_dict.get('min_macos_version'),
				valid_python_tags=blext_spec_dict.get('supported_python_tags'),
				valid_abi_tags=blext_spec_dict.get('supported_abi_tags'),
			),
			'release_profile': release_profile,
			'id': project['name'],
			'name': blext_spec_dict['pretty_name'],
			'tagline': project['description'],
			'version': project['version'],
			'license': f'SPDX:{extension_license}',
			'blender_version_min': blext_spec_dict['blender_version_min'],
			'blender_version_max': blext_spec_dict['blender_version_max'],
			'permissions': blext_spec_dict.get('permissions'),
			'copyright': blext_spec_dict['copyright'],
			'maintainer': (
				f'{first_maintainer["name"]} <{first_maintainer["email"]}>'
				if first_maintainer is not None
				else None
			),
			'tags': blext_spec_dict.get('bl_tags'),
			'website': homepage,
		}

		# Inject Release Profile Overrides
		if release_profile is not None and release_profile.overrides:
			_spec_params.update(release_profile.overrides)
			return cls(**_spec_params)  # pyright: ignore[reportArgumentType]
		return cls(**_spec_params)  # pyright: ignore[reportArgumentType]

	@classmethod
	def from_proj_spec_path(
		cls,
		path_proj_spec: Path,
		*,
		path_uv_exe: Path,
		release_profile_id: extyp.StandardReleaseProfile | str | None,
	) -> typ.Self:
		"""Parse an extension specification from a compatible file.

		Args:
			path_proj_spec: Path to either a `pyproject.toml`, or `*.py` script with inline metadata.
			release_profile_id: Identifier for the release profile.
			path_uv_exe: Optional overriden path to a `uv` executable.
				_Generally sourced from `blext.ui.GlobalConfig.path_uv_exe`_.

		Raises:
			ValueError: If the `pyproject.toml` file cannot be loaded, or it does not contain the required tables and/or fields.
		"""
		if path_proj_spec.is_file():
			if path_proj_spec.name == 'pyproject.toml':
				with path_proj_spec.open('rb') as f:
					proj_spec_dict = tomllib.load(f)
			elif path_proj_spec.name.endswith('.py'):
				with path_proj_spec.open('r') as f:
					proj_spec_dict = parse_inline_script_metadata(
						py_source_code=f.read(),
					)

				if proj_spec_dict is None:
					msg = f'Could not find inline script metadata in "{path_proj_spec}" (looking for a `# /// script` block)`.'
					raise ValueError(msg)
			else:
				msg = f'Tried to load a Blender extension project specification from "{path_proj_spec}", but it is invalid: Only `pyproject.toml` and `*.py` scripts w/inline script metadata are supported.'
				raise ValueError(msg)
		else:
			msg = f'Tried to load a Blender extension project specification from "{path_proj_spec}", but no such file exists.'
			raise ValueError(msg)

		name_from_spec = proj_spec_dict.get('project', {}).get('name')  # pyright: ignore[reportAny]
		if name_from_spec is None:
			msgs = [
				'Extension has no `project.name` field.',
			]
			raise ValueError(*msgs)
		if not isinstance(name_from_spec, str):
			msgs = [
				'`project.name` is not a string.',
			]
			raise TypeError(*msgs)

		if (
			path_proj_spec.name == 'pyproject.toml'
			and not (path_proj_spec.parent / name_from_spec).is_dir()
		):
			msgs = [
				'Project extension package name did not match `project.name`.',
				'> **Remedies**:',
				f'> 1. Rename extension package to `{name_from_spec}/`',
				'> 1. Set `project.name` to the name of the extension package.',
			]
			raise ValueError(*msgs)

		if path_proj_spec.name.endswith(
			'.py'
		) and name_from_spec != path_proj_spec.name.removesuffix('.py'):
			msgs = [
				'Script extension name did not match `project.name`.',
				'> **Remedies**:',
				f'> 1. Rename `{path_proj_spec.name}` to `{name_from_spec}.py`',
				f'> 2. Set `project.name = {path_proj_spec.name.removesuffix(".py")}`.',
			]
			raise ValueError(*msgs)

		# Parse Extension Specification
		return cls.from_proj_spec_dict(
			proj_spec_dict,
			path_uv_exe=path_uv_exe,
			path_proj_spec=path_proj_spec,
			release_profile_id=release_profile_id,
		)

	####################
	# - Validation
	####################
	@pyd.model_validator(mode='before')
	@classmethod
	def set_default_granular_bl_platforms_to_universal(cls, data: typ.Any) -> typ.Any:  # pyright: ignore[reportAny]
		"""Set the default BLPlatforms to the largest common subset of platforms supported by given Blender versions."""
		if (isinstance(data, dict) and 'granular_bl_platforms' not in data) or data[
			'granular_bl_platforms'
		] is None:
			if (
				'blender_version_min' in data
				and isinstance(data['blender_version_min'], str)
				and (
					'blender_version_max' not in data
					or (
						'blender_version_max' in data
						and isinstance(data['blender_version_max'], str)
					)
				)
			):
				released_bl_versions = (
					extyp.BLReleaseOfficial.from_official_version_range(
						data['blender_version_min'],  # pyright: ignore[reportUnknownArgumentType]
						data.get('blender_version_max'),  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
					)
				)
				granular_bl_platforms = functools.reduce(
					lambda a, b: a | b,
					[
						released_bl_version.bl_version.valid_bl_platforms
						for released_bl_version in released_bl_versions
					],
				)
				data['granular_bl_platforms'] = granular_bl_platforms
			else:
				msg = (
					'blender_version_min must be given to deduce granular_bl_platforms'
				)
				raise ValueError(msg)

		return data  # pyright: ignore[reportUnknownVariableType]

	@pyd.model_validator(mode='after')
	def validate_tags_against_bl_versions(self) -> typ.Self:
		"""Validate that all extension tags can actually be parsed by all supported Blender versions."""
		if self.tags is not None:
			valid_tags = functools.reduce(
				lambda a, b: a & b,
				[bl_version.valid_extension_tags for bl_version in self.bl_versions],
			)

			if self.tags.issubset(valid_tags):
				return self
			msgs = [
				'The following extension tags are not valid in all supported Blender versions:',
				*[f'- `{tag}`' for tag in sorted(self.tags - valid_tags)],
			]
			raise ValueError(*msgs)
		return self
