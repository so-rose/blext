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

import typing as typ
from pathlib import Path

import cyclopts
import rich.markdown
from frozendict import frozendict

from blext import extyp, pack, pydeps, ui, uityp

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
		output: Write built extension to this file / folder.
		overwrite: Allow overwriting `.zip`.
		vendor: Include dependencies as wheels in the `.zip`.
			When `False`, write `uv.lock` to the extension.
		check_output: Run `blext check` on the packed `.zip`.
	"""
	blext_info = blext_info.parse_proj(proj)

	blext_location = blext_info.blext_location(global_config)
	blext_spec = blext_info.blext_spec(global_config)

	bl_versions = blext_info.bl_versions(global_config)

	####################
	# - Report BLVersion Selection(s)
	####################
	match blext_info.bl_version:
		case ():
			CONSOLE.print(
				rich.markdown.Markdown(
					'\n'.join(
						[
							f'Selected **all {len(bl_versions)} extension-supported Blender version** chunks:',
							*[
								f'- `{bl_version.version}`'
								for bl_version in sorted(
									bl_versions, key=lambda el: el.version
								)
							],
						]
					)
				)
			)

		case ('detect',):
			bl_version = next(iter(bl_versions))
			CONSOLE.print(
				rich.markdown.Markdown(
					f'Selected **detected local Blender version**: `{bl_version.version}`'
				)
			)

		case _:
			CONSOLE.print(
				rich.markdown.Markdown(
					'\n'.join(
						[
							f'Selected **{len(bl_versions)} Blender version** chunks:',
							*[
								f'- `{bl_version.version}`'
								for bl_version in sorted(
									bl_versions, key=lambda el: el.version
								)
							],
						]
					)
				)
			)

	####################
	# - Report BLPlatform Selection(s)
	####################
	match blext_info.bl_platform:
		case ():
			CONSOLE.print(
				rich.markdown.Markdown(
					'\n'.join(
						[
							f'Selected **all {len(blext_spec.bl_platforms)} extension-supported platforms**:',
							*[
								f'- `{bl_platform}`'
								for bl_platform in sorted(blext_spec.bl_platforms)
							],
						]
					)
				)
			)
		case ('detect',):
			bl_platform = next(iter(blext_spec.bl_platforms))
			CONSOLE.print(
				rich.markdown.Markdown(
					f'Selected **detected local Blender platform**: `{bl_platform}`'
				)
			)
		case _:
			CONSOLE.print(
				rich.markdown.Markdown(
					'\n'.join(
						[
							f'Selected **{len(blext_spec.bl_platforms)} Blender platforms**:',
							*[
								f'- `{bl_platform}`'
								for bl_platform in sorted(blext_spec.bl_platforms)
							],
						]
					)
				)
			)

	####################
	# - Select Paths
	####################
	# Packed .zip Paths
	if output:
		if len(bl_versions) == 1:
			bl_version = next(iter(bl_versions))
			path_zips: frozendict[extyp.BLVersion, Path] = frozendict(
				{bl_version: output}
			)
		else:
			msg = 'Cannot set filename of extension zip when building extension for multiple Blender versions.'
			raise ValueError(msg)
	else:
		path_zips = blext_info.path_zips(global_config)

	# Pre-Packed .zip Paths
	path_zip_prepacks = blext_info.path_zip_prepacks(global_config)
	if vendor:
		files_in_prepack = blext_spec.wheel_paths_to_prepack(
			path_wheels=blext_location.path_wheel_cache
		)
	else:
		raise NotImplementedError

	# Wheel Paths (Cached & To Download)
	wheels_in_cache = blext_spec.cached_wheels(
		path_wheels=blext_location.path_wheel_cache,
		bl_versions=bl_versions,
	)
	wheels_to_download = blext_spec.missing_wheels(
		path_wheels=blext_location.path_wheel_cache,
		bl_versions=bl_versions,
	)

	####################
	# - Download Wheels
	####################
	if wheels_in_cache:
		CONSOLE.print(
			f'Found [bold]{len(wheels_in_cache)} wheel(s)[/bold] in download cache'
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

	if wheels_to_download:
		CONSOLE.print(f'Downloaded [bold]{len(wheels_to_download)} wheel(s)[/bold]')

	####################
	# - Pre-Pack Extension
	####################
	for bl_version in bl_versions:
		files_in_prepack_cache = pack.existing_prepacked_files(
			files_in_prepack[bl_version], path_zip_prepack=path_zip_prepacks[bl_version]
		)
		if files_in_prepack_cache:
			CONSOLE.print(
				f'Found [bold]{len(files_in_prepack_cache)} file(s)[/bold] in pre-pack cache for Blender version(s) `{bl_version.version}`'
			)

		files_to_prepack = {
			path: zipfile_path
			for path, zipfile_path in files_in_prepack[bl_version].items()
			if zipfile_path not in files_in_prepack_cache
		}
		with ui.ui_prepack_extension(
			files_to_prepack,
			console=CONSOLE,
		) as ui_callbacks:
			pack.prepack_extension(
				files_to_prepack,
				path_zip_prepack=path_zip_prepacks[bl_version],
				cb_pre_file_write=ui_callbacks.cb_pre_file_write,  # pyright: ignore[reportArgumentType]
				cb_post_file_write=ui_callbacks.cb_post_file_write,  # pyright: ignore[reportArgumentType]
			)

		if files_in_prepack:
			CONSOLE.print(
				f'Pre-packed [bold]{len(files_to_prepack)} file(s)[/bold] for Blender version(s) `{bl_version.version}`'
			)

	####################
	# - Pack Extension
	####################
	for bl_version in bl_versions:
		pack.pack_bl_extension(
			blext_spec,
			bl_version=bl_version,
			overwrite=overwrite,
			path_zip_prepack=path_zip_prepacks[bl_version],
			path_zip=path_zips[bl_version],
			path_pysrc=blext_location.path_pysrc(blext_spec.id),
		)

	####################
	# - Check Extension
	####################
	if check_output:
		for bl_version in bl_versions:
			check(
				blext_info=uityp.BLExtUI(path=path_zips[bl_version]),
				global_config=global_config,
			)

	####################
	# - Report Success
	####################
	CONSOLE.print()
	CONSOLE.print(
		rich.markdown.Markdown(
			'\n'.join(
				[
					f'Built extension [bold]{blext_spec.id}[/bold] to:',
					*[
						f'- `{bl_version.version}`: {path_zips[bl_version]}`'
						for bl_version in blext_info.bl_versions(global_config)
					],
				]
			)
		)
	)
