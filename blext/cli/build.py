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

"""Implements `blext build`."""

import shutil
import typing as typ
from pathlib import Path

import cyclopts
import rich.markdown

from blext import pack, pydeps, ui, uityp

from ._context import (
	APP,
	CONSOLE,
	DEFAULT_BLEXT_INFO,
	DEFAULT_CONFIG,
	ParameterBLExtInfo,
	ParameterConfig,
	ParameterProj,
)
from .check import check


@APP.command()
def build(  # noqa: C901, PLR0912, PLR0913, PLR0915
	proj: ParameterProj = None,
	*,
	blext_info: ParameterBLExtInfo = DEFAULT_BLEXT_INFO,
	global_config: ParameterConfig = DEFAULT_CONFIG,
	output: typ.Annotated[
		Path | None,
		cyclopts.Parameter(name=['--output', '-o']),
	] = None,
	overwrite: bool = True,
	vendor: bool = True,
	check_output: bool = True,
) -> None:
	"""Build an extension project.

	Parameters:
		proj: Location specifier for `blext` projects.
		blext_info: Information used to find and load `blext` project.
		global_config: Loaded global configuration.
		output: Extension zipfile path(s) to build. Supports macros:

			- `%bl_version`: **Required** when selecting multiple Blender versions.
			- `%platform`: **Required** when selecting multiple platforms.
			- `%ext_id`: Equivalent to `project.name`.
			- `%ext_version`: Equivalent to `project.version`.
		overwrite: Allow overwriting `.zip`.
		vendor: Include dependencies as wheels in the `.zip`.
			When `False`, write `uv.lock` to the extension.
		check_output: Run `blext check` on the packed `.zip`.
	"""
	blext_info = blext_info.parse_proj(proj)
	blext_location = blext_info.blext_location(global_config)

	####################
	# - Parse Specification
	####################
	blext_spec = blext_info.blext_spec(global_config)

	####################
	# - Select BLVersions
	####################
	match blext_info.bl_version:
		case ():
			CONSOLE.print(
				rich.markdown.Markdown(
					'\n'.join([
						f'Selected **all {len(blext_spec.bl_versions)} ext-supported Blender version** chunk(s):',
						*[
							f'- `{bl_version.version}`'
							for bl_version in blext_spec.sorted_bl_versions
						],
					])
				),
				'',
			)

		case ('detect',):
			CONSOLE.print(
				rich.markdown.Markdown(
					f'Selected **detected local Blender version**: `{global_config.local_default_bl_version.version}`'
				)
			)

		case _:
			requested_bl_versions = blext_info.requested_bl_versions(global_config)
			CONSOLE.print(
				rich.markdown.Markdown(
					'\n'.join([
						f'Selected **{len(requested_bl_versions)} Blender versions**:',
						*[
							f'- `{bl_version.version}`'
							for bl_version in sorted(
								requested_bl_versions, key=lambda el: el.version
							)
						],
					])
				),
				'',
			)

	bl_versions = blext_info.bl_versions(global_config)

	####################
	# - Select BLPlatforms
	####################
	match blext_info.platform:
		case ():
			CONSOLE.print(
				rich.markdown.Markdown(
					'\n'.join([
						f'Selected **all {len(blext_spec.granular_bl_platforms)} ext-supported platform(s)**:',
						*[
							f'- `{granular_bl_platform}`'
							for granular_bl_platform in blext_spec.sorted_granular_bl_platforms
						],
					])
				),
				'',
			)
		case ('detect',):
			CONSOLE.print(
				rich.markdown.Markdown(
					f'Selected **detected local Blender platform**: `{global_config.local_bl_platform}`'
				)
			)
		case _:
			requested_bl_platforms = blext_info.requested_bl_platforms(global_config)
			CONSOLE.print(
				rich.markdown.Markdown(
					'\n'.join([
						f'Selected **{len(requested_bl_platforms)} Blender platforms**:',
						*[
							f'- `{bl_platform}`'
							for bl_platform in sorted(requested_bl_platforms)
						],
					])
				),
				'',
			)

	bl_platforms = blext_info.bl_platforms(global_config)

	if any([
		blext_spec.deps.min_glibc_version is not None,
		blext_spec.deps.min_macos_version is not None,
		blext_spec.deps.valid_python_tags is not None,
		blext_spec.deps.valid_abi_tags is not None,
	]):
		if blext_spec.deps.min_glibc_version is not None:
			CONSOLE.print(
				rich.markdown.Markdown(
					f'Using **modified platform support** `min_glibc_version={list(blext_spec.deps.min_glibc_version)}`'
				)
			)
		if blext_spec.deps.min_macos_version is not None:
			CONSOLE.print(
				rich.markdown.Markdown(
					f'Using **modified platform support**: `min_macos_version={list(blext_spec.deps.min_macos_version)}`'
				)
			)
		if blext_spec.deps.valid_python_tags is not None:
			CONSOLE.print(
				rich.markdown.Markdown(
					f'Using **modified platform support**: `valid_python_tags={sorted(blext_spec.deps.valid_python_tags)}`'
				)
			)
		if blext_spec.deps.valid_abi_tags is not None:
			CONSOLE.print(
				rich.markdown.Markdown(
					f'Using **modified platform support**: `valid_abi_tags={sorted(blext_spec.deps.valid_abi_tags)}`'
				)
			)

		CONSOLE.print()

	####################
	# - Select Zip Path(s)
	####################
	path_zips = blext_info.path_zips(global_config)
	path_zip_prepacks = blext_info.path_zip_prepacks(global_config)

	# Select Final Zip Paths
	## Extensions are always built in the "build cache".
	## However, afterwards, they are optionally moved somewhere else.
	## That "somewhere else" is specified by the user as `output`.
	if output:
		if len(bl_versions) > 1 and '%bl_version' not in str(output):
			msgs = [
				'`--output` must contain a string `%bl_version`, when more than one Blender version chunk is selected.',
				'> **Remedies**:',
				'> 1. Add a string `%bl_version` to `--output`, so that extensions for different Blender versions can be built to different `.zip` files.',
				'> 2. Manually select a single `--bl-version`, so that the `BLVersion` can be unambiguously determined.',
			]
			raise ValueError(*msgs)

		if len(bl_platforms) > 1 and '%platform' not in str(output):
			msgs = [
				'`--output` must contain a string `%platform`, when more than one platform is selected.',
				'> **Remedies**:',
				'> 1. Add a string `%platform` to `--output`, so that extensions for different platforms can be built to different `.zip` files.',
				'> 2. Manually select a single `--platform`, so that the platform can be unambiguously determined.',
			]
			raise ValueError(*msgs)

		path_final_zips = {
			bl_version: {
				bl_platform: Path(*[
					(
						path_part.replace('%ext_id', str(blext_spec.id))
						.replace(
							'%ext_version', str(blext_spec.version).replace('.', '-')
						)
						.replace('%bl_version', bl_version.version.replace('.', '-'))
						.replace('%platform', bl_platform)
						.replace('%default', bl_platform)
					)
					for path_part in output.parts
				])
				for bl_platform in bl_platforms
			}
			for bl_version in bl_versions
		}
	else:
		path_final_zips = blext_info.path_final_zips(global_config)

	####################
	# - Select Filesystem Resources
	####################
	# Select Files to Pre-Pack
	## TODO: Use spec to query a cache-file tracker.
	if vendor:
		files_in_prepack = blext_spec.wheel_paths_to_prepack(
			path_wheels=blext_location.path_wheel_cache
		)
	else:
		raise NotImplementedError

	# Select Wheels to Download
	wheels_in_cache = blext_spec.query_cached_wheels(
		path_wheels=blext_location.path_wheel_cache,
		bl_versions=frozenset(bl_versions),
	)
	wheels_to_download = blext_spec.query_missing_wheels(
		path_wheels=blext_location.path_wheel_cache,
		bl_versions=frozenset(bl_versions),
	)

	####################
	# - Download Wheels
	####################
	CONSOLE.print(
		rich.markdown.Markdown(f'Found **{len(wheels_in_cache)} wheel(s)** in cache')
	)

	with ui.ui_download_wheels(
		wheels_to_download,
		console=CONSOLE,
	) as ui_callbacks:
		pydeps.download_wheels(
			wheels_to_download,
			path_wheels=blext_location.path_wheel_cache,
			cb_start_wheel_download=ui_callbacks.cb_start_wheel_download,
			cb_update_wheel_download=ui_callbacks.cb_update_wheel_download,
			cb_finish_wheel_download=ui_callbacks.cb_finish_wheel_download,
		)

	CONSOLE.print(
		rich.markdown.Markdown(f'Downloaded **{len(wheels_to_download)} wheel(s)**')
	)

	####################
	# - Pre-Pack Extension
	####################
	for bl_version in bl_versions:
		for bl_platform in bl_platforms:
			bl_platform_str = 'all' if len(bl_platforms) == 1 else str(bl_platform)

			CONSOLE.print()
			CONSOLE.print(
				rich.markdown.Markdown(
					f'**Pre-Packing** for `{bl_version.version}'
					+ (f':{bl_platform_str}`' if len(bl_platforms) > 1 else '`')
				)
			)
			files_in_prepack_cache = pack.existing_prepacked_files(
				files_in_prepack[bl_version][bl_platform],
				path_zip_prepack=path_zip_prepacks[bl_version][bl_platform],
			)
			CONSOLE.print(
				rich.markdown.Markdown(
					f'Found **{len(files_in_prepack_cache)} pre-packed file(s)** in cache'
				)
			)

			files_to_prepack = {
				path: path_inzip
				for path, path_inzip in files_in_prepack[bl_version][
					bl_platform
				].items()
				if path_inzip not in files_in_prepack_cache
			}
			with ui.ui_prepack_extension(
				files_to_prepack,
				console=CONSOLE,
			) as ui_callbacks:
				pack.prepack_extension(
					files_to_prepack,
					path_zip_prepack=path_zip_prepacks[bl_version][bl_platform],
					cb_pre_file_write=ui_callbacks.cb_pre_file_write,  # pyright: ignore[reportArgumentType]
					cb_post_file_write=ui_callbacks.cb_post_file_write,  # pyright: ignore[reportArgumentType]
				)

			CONSOLE.print(
				rich.markdown.Markdown(
					f'Pre-Packed **{len(files_to_prepack)} file(s)**'
				)
			)

	####################
	# - Pack Extension
	####################
	for bl_version in bl_versions:
		for bl_platform in bl_platforms:
			# Build Extension to Build Cache Dir
			pack.pack_bl_extension(
				blext_spec,
				bl_version=bl_version,
				bl_platform=bl_platform,
				overwrite=overwrite,
				path_zip_prepack=path_zip_prepacks[bl_version][bl_platform],
				path_zip=path_zips[bl_version][bl_platform],
				path_pysrc=blext_location.path_pysrc(blext_spec.id),
			)

			# Move Extension from Build Cache Dir to Build Dir
			if not path_final_zips[bl_version][bl_platform].parent.is_dir():
				path_final_zips[bl_version][bl_platform].parent.mkdir(
					parents=True, exist_ok=True
				)
			if (
				path_zips[bl_version][bl_platform]
				!= path_final_zips[bl_version][bl_platform]
			):
				shutil.move(
					path_zips[bl_version][bl_platform],
					path_final_zips[bl_version][bl_platform],
				)

	####################
	# - Report Success
	####################
	CONSOLE.print()
	CONSOLE.print(
		rich.markdown.Markdown(
			'\n'.join([
				f'Built extension(s) for `{blext_spec.id}`:',
				'',
				*[
					'\n'.join([
						f'- {path_final_zips[bl_version][bl_platform]}',
						'',
					])
					for bl_version in bl_versions
					for bl_platform in bl_platforms
				],
			])
		)
	)

	####################
	# - Check Extension
	####################
	if check_output:
		for bl_version in bl_versions:
			for bl_platform in bl_platforms:
				check(
					blext_info=uityp.BLExtUI(
						path=path_final_zips[bl_version][bl_platform]
					),
					global_config=global_config,
				)
