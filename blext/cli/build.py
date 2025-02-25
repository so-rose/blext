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

"""Implements the `build` command."""

import typing as typ
from pathlib import Path

import pydantic as pyd

import blext.exceptions as exc
from blext import blender, extyp, finders, loaders, pack, paths, pydeps, ui

from ._context import APP, CONSOLE


@APP.command()
def build(
	proj: Path | None = None,
	*,
	platform: extyp.BLPlatform | typ.Literal['detect'] | None = None,
	profile: extyp.StandardReleaseProfile | str = 'release',
	output: Path | None = None,
	overwrite: bool = True,
	vendor: bool = True,
) -> None:
	"""[Build] extension project to installable `.zip`.

	Parameters:
		proj: Path to Blender extension project.
		platform: Platform to build extension for.
			"detect" uses the current platform.
		profile: Initial settings to build extension with.
			Alters `initial_setings.toml` in the extension.
		output: Extension `.zip` to build.
			Folder path can also be specified.
		overwrite: Allow overwriting `.zip`.
		vendor: Include dependencies as wheels in the `.zip`.
			When `False`, write `uv.lock` to the extension.
	"""
	try:
		blender_exe = finders.find_blender_exe()
	except ValueError:
		blender_exe = None

	####################
	# - Parse Specification and Paths
	####################
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		blext_spec = loaders.load_bl_platform_into_spec(
			loaders.load_blext_spec(
				proj_uri=proj,
				release_profile_id=profile,
			),
			bl_platform_ref=platform,
		)

	if platform is None:
		CONSOLE.print(
			f'Selected [bold]all {len(blext_spec.bl_platforms)} extension-supported platform(s)[/bold]: [italic]{", ".join(sorted(blext_spec.bl_platforms))}[/italic]'
		)
	elif platform == 'detect':
		CONSOLE.print(
			f'Selected [bold]local detected platform[/bold]: [italic]{next(iter(blext_spec.bl_platforms))}[/italic]'
		)
	else:
		CONSOLE.print(
			f'Selected [bold]{len(blext_spec.bl_platforms)} platform(s)[/bold]: [italic]{", ".join(sorted(blext_spec.bl_platforms))}[/italic]'
		)

	path_wheels = paths.path_wheels(blext_spec)
	path_zip_prepack = paths.path_prepack(blext_spec) / blext_spec.packed_zip_filename
	path_zip = (
		paths.path_build(blext_spec) / blext_spec.packed_zip_filename
		if output is None
		else (output / blext_spec.packed_zip_filename if output.is_dir() else output)
	)
	path_pypkg = paths.path_pypkg(blext_spec)
	path_pysrc = paths.path_pysrc(blext_spec)

	####################
	# - Download Wheels
	####################
	wheels_from_cache = blext_spec.wheels_graph.wheels_from_cache(path_wheels)
	wheels_to_download = blext_spec.wheels_graph.wheels_to_download_to(path_wheels)

	if wheels_from_cache:
		CONSOLE.print(
			f'Found [bold]{len(wheels_from_cache)} wheel(s)[/bold] in download cache'
		)

	with ui.ui_download_wheels(
		wheels_to_download,
		console=CONSOLE,
	) as ui_callbacks:
		pydeps.network.download_wheels(
			wheels_to_download,
			path_wheels=path_wheels,
			cb_start_wheel_download=ui_callbacks.cb_start_wheel_download,
			cb_update_wheel_download=ui_callbacks.cb_update_wheel_download,
			cb_finish_wheel_download=ui_callbacks.cb_finish_wheel_download,
		)

	if wheels_to_download:
		CONSOLE.print(f'Downloaded [bold]{len(wheels_to_download)} wheel(s)[/bold]')

	####################
	# - Pre-Pack the Blender Extension
	####################
	if vendor:
		files_to_prepack = blext_spec.wheels_graph.wheel_paths_to_prepack(path_wheels)
	else:
		files_to_prepack = {paths.path_uv_lock(blext_spec): Path('uv.lock')}

	with ui.ui_prepack_extension(
		files_to_prepack,
		console=CONSOLE,
	) as ui_callbacks:
		prepacked_files = pack.prepack_extension(
			files_to_prepack,
			path_zip_prepack=path_zip_prepack,
			cb_pre_file_write=ui_callbacks.cb_pre_file_write,
			cb_post_file_write=ui_callbacks.cb_post_file_write,
		)

	if prepacked_files:
		CONSOLE.print(f'Pre-packed [bold]{len(prepacked_files)} file(s)[/bold]')

	####################
	# - Pack the Blender Extension
	####################
	with exc.handle(exc.pretty, ValueError):
		pack.pack_bl_extension(
			blext_spec,
			overwrite=overwrite,
			path_zip_prepack=path_zip_prepack,
			path_zip=path_zip,
			path_pypkg=path_pypkg,
			path_pysrc=path_pysrc,
		)

	####################
	# - Validate Extension Officially
	####################
	if blender_exe is not None:
		with exc.handle(exc.pretty, ValueError):
			blender.validate_extension(blender_exe, path_zip=path_zip)

	####################
	# - Report Success
	####################
	CONSOLE.print()
	CONSOLE.print(f'Built extension [bold]{blext_spec.id}[/bold]:', path_zip)
