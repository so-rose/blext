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
import packaging.utils
import pydantic as pyd
from frozendict import frozendict

from blext import extyp
from blext.utils.pydantic_frozendict import FrozenDict

from .pydep import PyDep
from .pydep_marker import PyDepMarker
from .pydep_wheel import PyDepWheel


class BLExtDeps(pyd.BaseModel, frozen=True):
	"""All Python dependencies needed by a Blender extension."""

	pydeps: FrozenDict[tuple[str, str], PyDep] = frozendict()
	target_pydeps: FrozenDict[str, PyDepMarker | None] = frozendict()

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
				(pydep_name, pydep_version),
				{'pydep': pydep},
			)
			for (pydep_name, pydep_version), pydep in self.pydeps.items()
		)

		## Add Edges w/Markers
		## - Each edge may have a "marker" denoting a conditional dependency.
		pydeps_graph.add_edges_from(  # pyright: ignore[reportUnknownMemberType]
			(
				(
					pydep_upstream_name,
					pydep_upsteam_version,
				),
				(pydep_downstream_name, pydep_downstream_version),
				{'marker': dependency_marker},
			)
			for (
				pydep_downstream_name,
				pydep_downstream_version,
			), pydep_downstream in self.pydeps.items()
			for pydep_upstream_name, dependency_marker in pydep_downstream.deps.items()
			for pydep_upsteam_version in [
				pydep_version
				for pydep_name, pydep_version in self.pydeps
				if pydep_upstream_name == pydep_name
			]
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
		# Buckle up kids!
		## I confused myself repeatedly, so I wrote some comments to help myself.
		## The journey begins with a quick little check.
		if bl_platform not in bl_version.valid_bl_platforms:
			msg = f'The given `bl_platform` in `{bl_platform}` is not supported by the given Blender version (`{bl_version.pretty_version}`).'
			raise ValueError(msg)

		# Now a function. Getting spicier!
		## Go read the documentation below. It's made with love <3
		def filter_edge(
			node_upstream: tuple[str, str],
			node_downstream: tuple[str, str],
		) -> bool:
			"""Don't follow dependency-edges with incompatible environment markers.

			Notes:
				Many PyDeps will include a dependency "only if" something is true.
				For example, "only if" on Windows.
				Naturally, this presents a complication: **How do we know what the end-user's Python environment is like**?

				Luckily, `bl_version` and `bl_platform` provide a nearly-complete description of the end-user's Python environment.

				Using this, we can evaluate any markers against the theoretical end-user Python environment, thus providing a dependency graph traversal that is correct for the given parameters.
			"""
			pydep_marker = self.pydeps_graph[node_upstream][node_downstream]['marker']  # pyright: ignore[reportAny, reportUnknownMemberType]

			return pydep_marker is None or pydep_marker.is_valid_for(  # pyright: ignore[reportAny]
				pkg_name=pkg_name,
				bl_version=bl_version,
				bl_platform=bl_platform,
			)

		# Now, let's deduce which 'pydep_name's the user actually asked for.
		## **If** the user specified markers, then we check and respect them.
		## **Don't** include targets that are vendored by Blender.
		pydep_target_names = {
			pydep_target_name
			for pydep_target_name, pydep_marker in self.target_pydeps.items()
			if (
				# The `pydep_name` may not be one of the BLVersion's vendored site-packages.
				## If it is, we don't error - we just do nothing; let Blender provide it.
				pydep_target_name not in bl_version.vendored_site_packages
				# Should there be a (user-defined) marker, we naturally make sure it's valid.
				## This is the one case not covered by `filter_edge`.
				and (
					pydep_marker is None
					or pydep_marker.is_valid_for(
						pkg_name=pkg_name,
						bl_version=bl_version,
						bl_platform=bl_platform,
					)
				)
			)
		}
		## NOTE: Blender-vendored pydeps are allowed to only have an sdist.
		## - Blender does a lot of its own building of dependencies.
		## - This is sensible. Look what we have to do to play with pydeps.
		## - But, not all of Blender's site-package have wheels.
		## - In fact, not all of them are on PyPi at all.
		## - This makes it difficult to duplicate Blender Python environment.
		## - (Need it be so?)
		## - We deal with this by never letting them progress to "finding wheels"...
		## - ...since no wheels would be able to be found.
		## - This works. Kind of. Egh.
		##
		## Dear Blender Devs: I beg you to run a PyPi repo for your homebrew builds.
		## - That way we can all just pin your repo...
		## - ...and easily duplicate Blender's Python environment.
		## - How-To for Gitea: https://docs.gitea.com/1.18/packages/packages/pypi
		## - I love you all <3. And thank you for coming to my TED Talk.

		# We need a fuller story than just `pydep_name` - we need (pydep_name, pydep_version)!
		## There should be exactly one of these, otherwise something is very wrong.
		## That's why you're here, isn't it? *Sigh*.
		pydep_targets: set[tuple[str, str]] = set()
		for pydep_target_name in pydep_target_names:
			all_targets_for_name = [
				(pydep_target_name, pydep_version)
				for pydep_name, pydep_version in self.pydeps
				if pydep_target_name == pydep_name
			]

			if len(all_targets_for_name) == 1:
				pydep_targets.add(all_targets_for_name[0])

			else:
				amount_str = 'More than one' if len(all_targets_for_name) > 1 else 'No'
				msgs = [
					f'{amount_str} version of a user-provided target dependency `{pydep_target_name}` was found. **This is a bug in `blext`**.',
					f'> - **Version**: `{bl_version}`',
					f'> - **Platform**: `{bl_platform}`',
					f'> - **Target Name**: `{pydep_target_name}`',
					'> - **Found Targets**:',
					*[
						f'>     {i}. `{pydep_target}`'
						for i, pydep_target in enumerate(all_targets_for_name)
					],
				]
				raise ValueError(*msgs)

		# Compute non-vendored ancestors of all target (pydep_name, pydep_version).
		## Now that we have the targets, we need to recursively find all their dependencies.
		## This includes checking each edge for marker validity.
		## No need to refer to Knuth. Just `nx.ancestors` and `nx.subgraph_view`.
		## `networkx` is really nice, did I mention that?
		valid_pydep_ancestors: set[tuple[str, str]] = {
			(pydep_ancestor_name, pydep_ancestor_version)
			for pydep_target_name, pydep_target_version in pydep_targets
			for pydep_ancestor_name, pydep_ancestor_version in nx.ancestors(  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
				nx.subgraph_view(
					self.pydeps_graph,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
					filter_edge=filter_edge,
				),
				(pydep_target_name, pydep_target_version),
			)
			if pydep_ancestor_name not in bl_version.vendored_site_packages
		}

		# You've found a return statement.
		## But will you ever be the same?
		## For now, have a cookie.
		return frozendict({
			pydep_name: self.pydeps[(pydep_name, pydep_version)]
			for pydep_name, pydep_version in sorted(
				pydep_targets | valid_pydep_ancestors,
				## NOTE: Neither has elements from bl_version.vendored_site_packages.
			)
		})

	####################
	# - Pydeps to PyDepWheels
	####################
	def wheels_by(
		self,
		*,
		pkg_name: str,
		bl_version: extyp.BLVersion,
		bl_platform: extyp.BLPlatform,
		err_msgs: dict[extyp.BLVersion, dict[extyp.BLPlatform, list[str]]]
		| None = None,
		err_num_missing_wheels: dict[extyp.BLVersion, dict[extyp.BLPlatform, int]]
		| None = None,
	) -> frozenset[PyDepWheel]:
		"""All wheels needed for a Blender extension.

		Notes:
			Computed from `self.validated_graph`.
		"""
		# I know it looks like a monster, but give it a chance, eh?
		## Even monsters deserve love. [1]
		## [1]: Shrek (2001)
		wheels = {
			pydep: pydep.select_wheel(
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
				target_descendants=frozenset({  # pyright: ignore[reportUnknownArgumentType]
					node
					for node in nx.descendants(  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
						self.pydeps_graph,  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
						(pydep.name, pydep.version_string),
					)
					if self.pydeps_graph.out_degree(node) == 0  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
				}),
				err_msgs=err_msgs[bl_version] if err_msgs is not None else None,
			)
			for pydep in self.pydeps_by(
				pkg_name=pkg_name,
				bl_version=bl_version,
				bl_platform=bl_platform,
			).values()
		}

		# Return the monster if every pydep/platform has a wheel.
		num_missing_wheels = sum(1 if wheel is None else 0 for wheel in wheels.values())
		if num_missing_wheels == 0:
			return frozenset(wheels.values())  # pyright: ignore[reportReturnType]

		# Otherwise, if error-passthrough is enabled, trust the caller to make good decisions.
		if err_msgs is not None and err_num_missing_wheels is not None:
			err_num_missing_wheels[bl_version][bl_platform] = num_missing_wheels
			return frozenset[PyDepWheel](
				filter(  # pyright: ignore[reportArgumentType]
					lambda el: el is not None,
					wheels.values(),
				)
			)

		msg = f'While running `deps.wheels_by`, `{num_missing_wheels}` wheels were missing from `{bl_version}:{bl_platform}`.'
		raise ValueError(msg)

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
		####################
		# - Stage 1: Parse [[package]]
		####################
		## - Projects: [[package]] list has extension package AND only upstream dependencies.
		## - Single-File Scripts: [[package]] list has only upstream dependencies.
		if 'package' not in uv_lock:
			pydeps: dict[tuple[str, str], PyDep] = {}  ## No PyDeps
		else:
			pydeps_set = {
				PyDep(
					name=package['name'],  # pyright: ignore[reportAny]
					version_string=package['version'],  # pyright: ignore[reportAny]
					registry=package['source']['registry'],  # pyright: ignore[reportAny]
					wheels=frozenset({
						PyDepWheel(
							url=wheel_info['url'],  # pyright: ignore[reportAny]
							registry=package['source']['registry'],  # pyright: ignore[reportAny]
							hash=wheel_info.get('hash'),  # pyright: ignore[reportAny]
							size=wheel_info.get('size'),  # pyright: ignore[reportAny]
						)
						for wheel_info in package.get('wheels', [])  # pyright: ignore[reportAny]
						if 'url' in wheel_info
					}),
					deps=frozendict({
						dependency['name']: (
							PyDepMarker(marker_str=dependency['marker'])  # pyright: ignore[reportAny]
							if 'marker' in dependency
							else None
						)
						for dependency in [  # pyright: ignore[reportAny]
							# Always include mandatory dependencies.
							*package.get('dependencies', []),  # pyright: ignore[reportAny]
							# Always include "all" optional dependencies.
							## - uv has already worked out which optional deps are needed.
							## - Unused [optional-dependencies] simply aren't in uv.lock.
							## - So, it's safe to pretend that they are all normal dependencies.
							*[
								resolved_opt_dependency
								for resolved_opt_dependencies in package.get(  # pyright: ignore[reportAny]
									'optional-dependencies',
									{},
								).values()
								for resolved_opt_dependency in resolved_opt_dependencies  # pyright: ignore[reportAny]
							],
						]
					}),
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
					# Package must not be the "current" package.
					## - We've made the decision not to consider the root (L0) package as a PyDep.
					and packaging.utils.canonicalize_name(module_name)
					!= packaging.utils.canonicalize_name(package['name'])  # pyright: ignore[reportAny]
				)
			}
			pydeps = {(pydep.name, pydep.version_string): pydep for pydep in pydeps_set}

		####################
		# - Stage 2: Parse Target (L1) Dependencies
		####################
		## The L0 (root) PyDep is the blext project itself, pulling in all other PyDeps.
		## The L1 (target) PyDeps are all of the immediate user-requested PyDeps (were 'uv add'ed).
		## L1 PyDeps come in "groups" such as '_' (default), 'dev', and also Blender version-specific.

		target_pydeps: dict[str, PyDepMarker | None] = {}

		# Single-File Scripts: [manifest] table has top-level dependencies - make a "fake" PyDep.
		if 'manifest' in uv_lock:
			# Parse Mandatory Dependencies
			## - Always found in 'manifest.requirements'.
			if 'requirements' in uv_lock['manifest']:
				target_pydeps = {
					packaging.utils.canonicalize_name(
						dependency['name']  ## pyright: ignore[reportAny]
					): None
					for dependency in uv_lock['manifest']['requirements']  # pyright: ignore[reportAny]
				}
			else:
				msg = '`uv.lock` has a `[manifest]`, but no `manifest.requirements`. Was it generated correctly?'
				raise RuntimeError(msg)

		# Projects: Find L1 Deps from the L0 Dep (the root package == the blext project)
		elif 'package' in uv_lock:
			# Find the Root Package
			root_package: dict[str, typ.Any] = next(
				package
				for package in uv_lock['package']  # pyright: ignore[reportAny]
				if 'name' in package
				and module_name == packaging.utils.canonicalize_name(package['name'])  # pyright: ignore[reportAny]
			)

			# Parse Target Dependencies
			## - Always found in root_package['metadata']['requires-dist'].
			## - In `pyproject.toml`, they are given as 'project.dev-dependencies'.
			if (
				'metadata' in root_package
				and 'requires-dist' in root_package['metadata']
			):
				target_pydeps = {
					packaging.utils.canonicalize_name(dependency['name']): PyDepMarker(  # pyright: ignore[reportAny]
						marker_str=dependency['marker']  # pyright: ignore[reportAny]
					)
					if 'marker' in dependency
					else None
					for dependency in root_package['metadata']['requires-dist']  # pyright: ignore[reportAny]
				}
				## NOTE: It's safe to ignore 'extra'. uv.lock's resolution already managed this.

		return cls(
			pydeps=frozendict(pydeps),
			target_pydeps=frozendict(target_pydeps),
			min_glibc_version=min_glibc_version,
			min_macos_version=min_macos_version,
			valid_python_tags=valid_python_tags,
			valid_abi_tags=valid_abi_tags,
		)
