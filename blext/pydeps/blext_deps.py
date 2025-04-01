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

import networkx as nx
import pydantic as pyd
from frozendict import frozendict

from blext import extyp
from blext.utils.pydantic_frozendict import FrozenDict

from .pydep import PyDep
from .pydep_marker import PyDepMarker
from .pydep_wheel import PyDepWheel


class BLExtDeps(pyd.BaseModel, frozen=True):
	"""All Python dependencies needed by a Blender extension."""

	pydeps: FrozenDict[str, PyDep]
	target_pydeps: FrozenDict[str, PyDepMarker | None]

	# PyDepWheel Constraint Overrides
	## - 'None' will use the property from `bl_version`.
	min_glibc_version: tuple[int, int] | None = None
	min_macos_version: tuple[int, int] | None = None
	valid_python_tags: frozenset[str] | None = None
	valid_abi_tags: frozenset[str] | None = None

	####################
	# - PyDeps Dependency Graph
	####################
	@functools.cached_property
	def pydeps_graph(self) -> nx.DiGraph:  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
		"""Dependency-graph representation of `self.pydeps`."""
		pydeps_graph = nx.DiGraph()  # pyright: ignore[reportUnknownVariableType]

		## Add Nodes as Package Names
		## - Each node is annotated with a PyDepPyDepWheel
		pydeps_graph.add_nodes_from(  # pyright: ignore[reportUnknownMemberType]
			(
				pydep_name,
				{'pydep': pydep},
			)
			for pydep_name, pydep in self.pydeps.items()
		)

		## Add Edges w/Markers
		## - Each edge may have a "marker" denoting a conditional dependency.
		pydeps_graph.add_edges_from(  # pyright: ignore[reportUnknownMemberType]
			(
				pydep_upstream_name,
				pydep_downstream_name,
				{'marker': dependency_marker},
			)
			for pydep_downstream_name, pydep_downstream in self.pydeps.items()
			for pydep_upstream_name, dependency_marker in pydep_downstream.pydep_markers
		)

		return pydeps_graph  # pyright: ignore[reportUnknownVariableType]

	####################
	# - PyDeps Filtering
	####################
	def pydeps_by(
		self,
		*,
		pkg_name: str,
		bl_version: extyp.BLVersion,
		bl_platform: extyp.BLPlatform,
	) -> frozendict[str, PyDep]:
		"""All Python dependencies needed by the given Python environment."""

		def filter_edge(node_upstream: str, node_downstream: str) -> bool:
			"""Checks if each marker is `None`, or valid, on the edge between upstream/downstream node."""
			pydep_marker: PyDepMarker | None = self.pydeps_graph[node_upstream][  # pyright: ignore[reportUnknownMemberType]
				node_downstream
			]['marker']

			return pydep_marker is None or pydep_marker.is_valid_for(
				pkg_name=pkg_name,
				bl_version=bl_version,
				bl_platform=bl_platform,
			)

		if bl_platform in bl_version.valid_bl_platforms:
			return frozendict(
				{
					self.pydeps[pydep_name]
					for pydep_name in (
						pydep_name
						for pydep_name, pydep_marker in self.target_pydeps.items()
						if pydep_marker is None
						or pydep_marker.is_valid_for(
							pkg_name=pkg_name,
							bl_version=bl_version,
							bl_platform=bl_platform,
						)
					)
					for pydep_name in nx.ancestors(  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
						nx.subgraph_view(
							self.pydeps_graph,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
							filter_edge=filter_edge,
						),
						pydep_name,
					)
					# TODO: Exclude each bl_version's no-no list.
					## - Also, some kind of error if someone's trying to include something from the no-no list.
				}
			)

		msg = f'Given `bl_platform` (`{bl_platform}`) is not supported by the given Blender version (`{bl_version.version}`).'
		raise ValueError(msg)

	####################
	# - Pydeps to PyDepWheels
	####################
	def wheels_by(
		self,
		*,
		pkg_name: str,
		bl_version: extyp.BLVersion,
		bl_platform: extyp.BLPlatform,
	) -> frozenset[PyDepWheel]:
		"""All wheels needed for a Blender extension.

		Notes:
			Computed from `self.validated_graph`.
		"""
		err_msgs: list[str] = []
		wheels: frozenset[PyDepWheel | None] = frozenset(
			{
				pydep.select_wheel(
					bl_platform=bl_platform,
					min_glibc_version=(
						bl_version.min_glibc_version
						if self.min_glibc_version is None
						else self.min_glibc_version
					),
					min_macos_version=(
						bl_version.min_macos_version
						if self.min_macos_version is None
						else self.min_macos_version
					),
					valid_python_tags=(
						bl_version.valid_python_tags
						if self.valid_python_tags is None
						else self.valid_python_tags
					),
					valid_abi_tags=(
						bl_version.valid_abi_tags
						if self.valid_abi_tags is None
						else self.valid_abi_tags
					),
					err_msgs=err_msgs,
				)
				for pydep in self.pydeps_by(
					pkg_name=pkg_name, bl_version=bl_version, bl_platform=bl_platform
				).values()
			}
		)
		if all(wheel is not None for wheel in wheels):
			return wheels  # pyright: ignore[reportReturnType]

		err_msgs.append(
			f'**Missing Dependencies**: {sum(wheel is None for wheel in wheels)}'
		)
		err_msgs.extend([])
		raise ValueError(*err_msgs)

	def total_size_bytes_by(
		self,
		*,
		pkg_name: str,
		bl_version: extyp.BLVersion,
		bl_platform: extyp.BLPlatform,
	) -> pyd.ByteSize:
		"""Total size of all wheels."""
		return pyd.ByteSize(
			sum(
				int(wheel.size)
				for wheel in self.wheels_by(
					pkg_name=pkg_name, bl_version=bl_version, bl_platform=bl_platform
				)
			)
		)

	####################
	# - Creation
	####################
	@classmethod
	def from_uv_lock(
		cls,
		uv_lock: frozendict[str, typ.Any],
		*,
		module_name: str,
		min_glibc_version: tuple[int, int] | None = None,
		min_macos_version: tuple[int, int] | None = None,
		valid_python_tags: frozenset[str] | None = None,
		valid_abi_tags: frozenset[str] | None = None,
	) -> typ.Self:
		"""Create from a `uv.lock` file.

		Parameters:
			uv_lock: Result of parsing a `uv.lock` file with ex. `tomllib`.
			module_name: Name of the top-level Python module, which depends on everything else.
				Should be identical to:
				- **Script Extensions**: The module name without `.py`, such that `<module_name>.py` exists.
				- **Project Extensions**: The package folder name, such that `<module_name>/__init__.py` exists and has the extension's `register()` method.
				- `BLExtSpec.id`: The
		"""

		@functools.cache
		def nrm_name(pkg_name: str) -> str:
			return pkg_name.replace('-', '_').lower()

		####################
		# - Stage 1: Parse [[package]]
		####################
		## - Projects: [[package]] list has extension package AND only upstream dependencies.
		## - Single-File Scripts: [[package]] list has only upstream dependencies.
		if 'package' not in uv_lock:
			pydeps: dict[str, PyDep] = {}  ## No PyDeps
		else:
			pydeps = {
				nrm_name(package['name']): PyDep(  # pyright: ignore[reportAny]
					name=nrm_name(package['name']),  # pyright: ignore[reportAny]
					version=package['version'],  # pyright: ignore[reportAny]
					registry=package['source']['registry'],  # pyright: ignore[reportAny]
					wheels=frozenset(
						{
							PyDepWheel(
								url=wheel_info['url'],  # pyright: ignore[reportAny]
								registry=package['source']['registry'],  # pyright: ignore[reportAny]
								hash=wheel_info.get('hash'),  # pyright: ignore[reportAny]
								size=wheel_info.get('size'),  # pyright: ignore[reportAny]
							)
							for wheel_info in package['wheels']  # pyright: ignore[reportAny]
							if 'url' in wheel_info
						}
					),
					pydep_markers=frozendict(
						{
							nrm_name(dependency['name']): (  # pyright: ignore[reportAny]
								PyDepMarker(marker_str=dependency['marker'])  # pyright: ignore[reportAny]
								if 'marker' in dependency
								else None,
							)
							for dependency in [  # pyright: ignore[reportAny]
								# Always include mandatory dependencies.
								*package['dependencies'],
								# Always include "all" optional dependencies.
								## - uv has already worked out which optional deps are needed.
								## - Unused [optional-dependencies] simply aren't in uv.lock.
								## - So, it's safe to pretend that they are all normal dependencies.
								*[
									resolved_opt_dependency
									for resolved_opt_dependencies in package[  # pyright: ignore[reportAny]
										'optional-dependencies'
									].values()
									for resolved_opt_dependency in resolved_opt_dependencies  # pyright: ignore[reportAny]
								],
							]
						}
					),
				)
				for package in uv_lock['package']  # pyright: ignore[reportAny]
				if (
					# Package must have a name.
					'name' in package
					# Package must have a version.
					and 'version' in package
					# Package must have a registry URL.
					and 'source' in package
					and 'registry' in package['source']
					# Package must have wheels.
					and 'wheels' in package
					# Package must not be the "current" package.
					## - We've made the decision not to consider the root (L0) package as a PyDep.
					and module_name != nrm_name(package['name'])  # pyright: ignore[reportAny]
				)
			}

		####################
		# - Stage 2: Parse Target (L1) Dependencies
		####################
		## - The L0 (root) PyDep is the blext project itself, pulling in all other PyDeps.
		## - The L1 (target) PyDeps are all of the immediate user-requested PyDeps (were 'uv add'ed).
		## - L1 PyDeps come in "groups" such as '_' (default), 'dev', and also Blender version-specific.

		target_pydeps: dict[str, PyDepMarker | None] = {}

		## - Single-File Scripts: [manifest] table has top-level dependencies - make a "fake" PyDep.
		if 'manifest' in uv_lock:
			# Parse Mandatory Dependencies
			## - Always found in 'manifest.requirements'.
			if 'requirements' in uv_lock['manifest']:
				target_pydeps = {
					dependency['name']: None
					for dependency in uv_lock['manifest']['requirements']  # pyright: ignore[reportAny]
				}
			else:
				msg = '`uv.lock` has a `[manifest]`, but no `manifest.requirements`. Was it generated correctly?'
				raise RuntimeError(msg)

		## - Projects: Find L1 Deps from the L0 Dep (the root package == the blext project)
		elif 'package' in uv_lock:
			# Find the Root Package
			root_package: dict[str, typ.Any] = next(
				package
				for package in uv_lock['package']  # pyright: ignore[reportAny]
				if 'name' in package and module_name == nrm_name(package['name'])  # pyright: ignore[reportAny]
			)

			# Parse Target Dependencies
			## - Always found in root_package['metadata']['requires-dist'].
			## - In `pyproject.toml`, they are given as 'project.dev-dependencies'.
			## - NOTE: It's safe to ignore 'extra', as this is already accounted for in uv.lock.
			if (
				'metadata' in root_package
				and 'requires-dist' in root_package['metadata']
			):
				target_pydeps = {
					nrm_name(dependency['name']): PyDepMarker(  # pyright: ignore[reportAny]
						marker_str=dependency['marker']  # pyright: ignore[reportAny]
					)
					if 'marker' in dependency
					else None
					for dependency in root_package['metadata']['requires-dist']  # pyright: ignore[reportAny]
				}

		return cls(
			pydeps=frozendict(pydeps),
			target_pydeps=frozendict(target_pydeps),
			min_glibc_version=min_glibc_version,
			min_macos_version=min_macos_version,
			valid_python_tags=valid_python_tags,
			valid_abi_tags=valid_abi_tags,
		)
