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

"""Tools for managing wheel-based dependencies."""

import functools
import typing as typ
from collections import defaultdict
from pathlib import Path

import pydantic as pyd
from frozendict import deepfreeze, frozendict

from blext import extyp

from .wheel import BLExtWheel


class BLExtWheelsGraph(pyd.BaseModel, frozen=True):
	"""A graph of Python dependencies needed by a Blender extension."""

	all_wheels: frozenset[BLExtWheel]

	min_glibc_version: tuple[int, int] = (2, 20)
	min_macos_version: tuple[int, int] = (11, 0)
	## TODO: Constrained integers for both
	## TODO: The "Blender version" itself has a certain support matrix. Perhaps it wouldn't be terrible to default to that?

	supported_bl_platforms: frozenset[extyp.BLPlatform]
	valid_python_tags: frozenset[str] = frozenset(
		{
			'py3',
			'cp36',
			'cp37',
			'cp38',
			'cp39',
			'cp310',
			'cp311',
		}
	)
	valid_abi_tags: frozenset[str] = frozenset({'none', 'abi3', 'cp311'})
	## TODO: Keep a "Blender version" instead, then reverse-engineer the Python version that it uses, then reverse-engineer valid Python/ABI tags from there.
	## - This is also nice, as it can allow for limited modification by the user ex. to allow older CPython versions that might technically work, but which are considered too iffy to use as a default.

	####################
	# - Wheel Reductions: Find Info Across Wheels
	####################
	@functools.cached_property
	def wheel_projects(self) -> frozenset[str]:
		"""All wheel dependency names aka. "projects"."""
		return frozenset({wheel.project for wheel in self.all_wheels})

	####################
	# - Wheel Mappings: Find Info per Wheel
	####################
	@functools.cached_property
	def wheel_bl_platforms(
		self,
	) -> frozendict[BLExtWheel, frozenset[extyp.BLPlatform]]:
		"""Compatible Blender platforms for each wheel."""
		return frozendict(
			{
				wheel: wheel.compatible_bl_platforms(
					valid_python_tags=self.valid_python_tags,
					valid_abi_tags=self.valid_abi_tags,
					min_glibc_version=self.min_glibc_version,
					min_macos_version=self.min_macos_version,
				)
				for wheel in self.all_wheels
			}
		)

	####################
	# - Wheel Indexings: Find Wheels w/Property
	####################
	@functools.cached_property
	def wheels_by_project(self) -> frozendict[str, frozenset[BLExtWheel]]:
		"""Search the graph for all wheels associated with a particular project (dependency name)."""
		return frozendict(
			{
				wheel_project: frozenset(
					{
						wheel
						for wheel in self.all_wheels
						if wheel.project == wheel_project
					}
				)
				for wheel_project in self.wheel_projects
			}
		)

	@functools.cached_property
	def wheels_by_bl_platform(
		self,
	) -> frozendict[extyp.BLPlatform, frozenset[BLExtWheel]]:
		"""Search the graph using semantic key values, yielding a set of matching wheels."""
		wheels_by_bl_platform: defaultdict[extyp.BLPlatform, set[BLExtWheel]] = (
			defaultdict(set)
		)
		for wheel, bl_platforms in self.wheel_bl_platforms.items():
			for bl_platform in bl_platforms:
				wheels_by_bl_platform[bl_platform].add(wheel)
		return deepfreeze(wheels_by_bl_platform)  #  pyright: ignore[reportAny]

	####################
	# - Wheel Graph
	####################
	@functools.cached_property
	def complete_graph(
		self,
	) -> frozendict[str, frozendict[extyp.BLPlatform, frozenset[BLExtWheel]]]:
		"""Represent wheels by project name and platform.

		This makes it easy to deduce whether a wheel is available for all Blender platforms one wishes to support.
		"""
		return deepfreeze(
			{
				wheel_project: {
					bl_platform: {
						wheel
						for wheel in self.wheels_by_bl_platform[bl_platform]
						if wheel_project == wheel.project
					}
					for bl_platform in self.supported_bl_platforms
				}
				for wheel_project in self.wheel_projects
			}
		)  #  pyright: ignore[reportAny]

	@functools.cached_property
	def validated_graph(
		self,
	) -> frozendict[str, frozendict[extyp.BLPlatform, BLExtWheel]]:
		# Construct Mutable Platform Graph
		## - A mutable, ordered copy preserves the cache semantics of complete_platform_graph.
		wheel_graph: dict[str, dict[extyp.BLPlatform, list[BLExtWheel]]] = {
			wheel_project: {
				bl_platform: list(wheels)
				for bl_platform, wheels in wheels_by_platform.items()
			}
			for wheel_project, wheels_by_platform in self.complete_graph.items()
		}

		####################
		# - Filter: Select ONE Wheel Per-Dependency Per-Platform
		####################
		for wheel_project, wheels_by_platform in wheel_graph.items():
			for bl_platform, wheels in wheels_by_platform.items():
				if len(wheels) > 1:
					# Linux
					if bl_platform in [
						extyp.BLPlatform.linux_x64,
						extyp.BLPlatform.linux_arm64,
					]:
						wheel_graph[wheel_project][bl_platform] = sorted(
							wheels,
							key=lambda wheel: wheel.sort_key_preferred_linux,
						)[:1]

					# MacOS: Sort by OS version and pick the highest valid version.
					elif bl_platform in [
						extyp.BLPlatform.macos_x64,
						extyp.BLPlatform.macos_arm64,
					]:
						wheel_graph[wheel_project][bl_platform] = sorted(
							wheels,
							key=lambda wheel: wheel.sort_key_preferred_mac,
						)[:1]

					# Windows
					elif bl_platform is extyp.BLPlatform.windows_x64:
						wheel_graph[wheel_project][bl_platform] = sorted(
							wheels,
							key=lambda wheel: wheel.sort_key_preferred_windows,
						)[:1]

		####################
		# - Validate: Ensure All Deps + Platforms Have ==1 Wheel
		####################
		num_missing_deps = 0
		missing_dep_msgs: list[str] = []
		for wheel_project, wheels_by_platform in wheel_graph.items():
			for bl_platform, wheels in wheels_by_platform.items():
				if len(wheels) == 0:
					# Increment Missing Dependency Count
					num_missing_deps += 1

					# Find All Candidate Wheels by Project (Dependency Name)
					wheels_by_project = sorted(
						self.wheels_by_project[wheel_project],
						key=lambda el: el.filename,
					)

					# Assemble Error Messages
					min_glibc_str = '.'.join(str(i) for i in self.min_glibc_version)
					min_macos_str = '.'.join(str(i) for i in self.min_macos_version)
					msgs = [
						f'**{wheel_project}** not found for `{bl_platform}`.',
						*(
							[
								'|  **Possible Causes**:',
								'|  - `...manylinux_M_m_<arch>.whl` wheels require `glibc >= M.m`.',
								f'|  - This extension is set to require `glibc >= {min_glibc_str}`.',
								f'|  - Therefore, only wheels with `macos <= {min_glibc_str}` can be included.',
								'|  ',
								'|  **Suggestions**:',
								'|  - Try raising `min_glibc_version = [M, m]` in `[tool.blext]`.',
								'|  - _This may make the extension incompatible with older machines_.',
							]
							if bl_platform.startswith('linux')
							else []
						),
						*(
							[
								'|  **Possible Causes**:',
								'|  - `...macosx_M_m_<arch>.whl` wheels require `macos >= M.m`.',
								f'|  - This extension is set to require `macos >= {min_macos_str}`.',
								f'|  - Therefore, only wheels with `macos <= {min_macos_str}` can be included.',
								'|  ',
								'|  **Suggestions**:',
								'|  - Try raising `min_macos_version = [M, m]` in `[tool.blext]`.',
								'|  - _This may make the extension incompatible with older machines_.',
							]
							if bl_platform.startswith('macos')
							else []
						),
						*(
							[
								'|  ',
								'|  **Rejected Wheels**:',
							]
							+ [
								f'|  - {candidate_wheel.filename}'
								for candidate_wheel in wheels_by_project
							]
						),
						'|',
					]
					for msg in msgs:
						missing_dep_msgs.append(msg)

				if len(wheels) > 1:
					msg = f">1 valid wheel is set to be downloaded for '{wheel_project}:{bl_platform}', which indicates a bug in 'blext'. Please report this bug!"
					raise RuntimeError(msg)

		# Display Error Messages
		if missing_dep_msgs:
			missing_dep_msgs.append(f'**Missing Dependencies**: {num_missing_deps}')
			raise ValueError(*missing_dep_msgs)

		####################
		# - Process and Return
		####################
		return frozendict(
			{
				wheel_project: frozendict(
					{
						bl_platform: wheels[0]
						for bl_platform, wheels in wheels_by_platform.items()
					}
				)
				for wheel_project, wheels_by_platform in wheel_graph.items()
			}
		)

	####################
	# - Processed Wheels
	####################
	@functools.cached_property
	def wheels(self) -> frozenset[BLExtWheel]:
		return frozenset(
			{
				wheel
				for _, wheels_by_platform in self.validated_graph.items()
				for _, wheel in wheels_by_platform.items()
			}
		)

	@functools.cached_property
	def total_size_bytes(self) -> pyd.ByteSize:
		return pyd.ByteSize(
			sum(
				int(wheel.size) if wheel.size is not None else 0
				for wheel in self.wheels
			)
		)

	####################
	# - Wheel Path Handling
	####################
	def wheels_from_cache(self, path_wheels: Path) -> frozenset[BLExtWheel]:
		"""Deduce which of `self.wheels` need to be downloaded, by comparing to wheels currently available in `path_wheels`."""
		wheel_filenames_existing = frozenset(
			{path_wheel.name for path_wheel in path_wheels.rglob('*.whl')}
		)
		return frozenset(
			{
				wheel
				for wheel in self.wheels
				if wheel.filename in wheel_filenames_existing
				## TODO: or existing hash no match
			}
		)

	def wheels_to_download_to(self, path_wheels: Path) -> frozenset[BLExtWheel]:
		"""Deduce which of `self.wheels` need to be downloaded, by comparing to wheels currently available in `path_wheels`."""
		wheel_filenames_existing = frozenset(
			{path_wheel.name for path_wheel in path_wheels.rglob('*.whl')}
		)
		return frozenset(
			{
				wheel
				for wheel in self.wheels
				if wheel.filename not in wheel_filenames_existing
				## TODO: or existing hash no match
			}
		)

	def wheel_paths_to_prepack(self, path_wheels: Path) -> dict[Path, Path]:
		"""Deduce a wheel path mapping suitable for packing into an extension `.zip`.

		Notes:
			Use the `|` dictionary operator to combine with other dictionaries specifying files to prepack.
		"""
		if not self.wheels_to_download_to(path_wheels):
			return {
				path_wheels / wheel.filename: Path('wheels') / wheel.filename
				for wheel in self.wheels_from_cache(path_wheels)
			}

		msg = 'Tried to get wheel paths for pre-packing, but not all required wheels are downloaded.'
		raise ValueError(msg)

	####################
	# - Creation
	####################
	@classmethod
	def from_uv_lock(
		cls,
		uv_lock: frozendict[str, typ.Any],
		*,
		supported_bl_platforms: frozenset[extyp.BLPlatform],
		min_glibc_version: tuple[int, int],
		min_macos_version: tuple[int, int],
	) -> typ.Self:
		# Parse Dependencies and Packages

		packages = tuple(
			[
				package
				for package in uv_lock['package']
				if 'name' in package
				and not (
					'source' in package
					and 'virtual' in package['source']
					and package['source']['virtual'] == '.'
				)
			]
		)

		# Parse Wheels: URL
		wheels_url = {
			BLExtWheel(
				url=wheel_info['url'],
				hash=wheel_info.get('hash'),
				size=wheel_info.get('size'),
			)
			for package in packages
			for wheel_info in package.get('wheels', [])
			if (
				'source' in package
				and 'registry' in package['source']
				and 'url' in wheel_info
			)
		}
		wheels_path_editable = {
			BLExtWheel(
				path=package['source']['editable'].resolve(),
			)
			for package in packages
			if ('source' in package and 'editable' in package['source'])
		}
		wheels_path_directory = {
			BLExtWheel(
				path=package['source']['directory'].resolve(),
			)
			for package in packages
			if ('source' in package and 'directory' in package['source'])
		}

		return cls(
			all_wheels=frozenset(
				wheels_url | wheels_path_editable | wheels_path_directory
			),
			supported_bl_platforms=supported_bl_platforms,
			min_glibc_version=min_glibc_version,
			min_macos_version=min_macos_version,
		)

	####################
	# - Convenience
	####################
	def search(self, key: extyp.BLPlatform | typ.Any) -> frozenset[BLExtWheel]:
		"""Search the graph using semantic key values, yielding a set of matching wheels."""
		if isinstance(key, extyp.BLPlatform):
			return self.wheels_by_bl_platform[key]

		msg = f'Could not search BLExtWheelGraph using `key = {key}`.'
		raise ValueError(msg)

	def __getitem__(self, key: extyp.BLPlatform | typ.Any) -> frozenset[BLExtWheel]:
		return self.search(key)
