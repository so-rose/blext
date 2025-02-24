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

import os
import typing as typ
from pathlib import Path

import pydantic as pyd
import rich.live
import rich.markdown
import rich.panel
import rich.progress
import rich.table

import blext.exceptions as exc
from blext import extyp, loaders, pack, paths, pydeps

from ._context import APP, CONSOLE


@APP.command()
def build(
	proj: Path | None = None,
	*,
	platform: extyp.BLPlatform | typ.Literal['detect'] | None = None,
	profile: extyp.StandardReleaseProfile | str = 'release',
	output: Path | None = None,
) -> None:
	"""[Build] the extension to an installable `.zip` file.

	Parameters:
		proj: Path to the Blender extension project.
		bl_platform: Blender platform(s) to constrain the extension to.
			Use "detect" to constrain to detect the current platform.
		profile: The release profile ID to apply to the extension.
	"""
	####################
	# - Build Extension
	####################
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		blext_spec = loaders.load_bl_platform_into_spec(
			loaders.load_blext_spec(
				proj_uri=proj,
				release_profile_id=profile,
			),
			bl_platform_ref=platform,
		)

		####################
		# - Download Wheels
		####################
		path_wheels = paths.path_wheels(blext_spec)
		existing_wheel_filenames = frozenset(
			{path_wheel.name for path_wheel in path_wheels.rglob('*.whl')}
		)
		wheels = frozenset(
			{
				wheel
				for wheel in blext_spec.wheels_graph.wheels
				if wheel.filename not in existing_wheel_filenames
			}
		)

		download_progress = rich.progress.Progress(
			rich.progress.SpinnerColumn(),
			'{task.description}',
			rich.progress.BarColumn(
				bar_width=None,
			),
			rich.progress.DownloadColumn(),
			expand=True,
			console=CONSOLE,
		)
		download_task = download_progress.add_task(
			'Downloading',
			total=int(blext_spec.wheels_graph.total_size_bytes)
			- sum(
				os.stat(path_wheel).st_size for path_wheel in path_wheels.rglob('*.whl')
			),
			start=True,
		)
		## TODO: total should be based on what's left to download

		max_wheel_project_length = (
			max(
				[
					max([len(wheel.project) for wheel in wheels] + [len('Name')]),
					len('Name'),
				]
			)
			+ 1
		)
		max_wheel_version_length = (
			max(
				[
					max([len(wheel.version) for wheel in wheels] + [len('Version')]),
					len('Version'),
				]
			)
			+ 1
		)
		max_wheel_tags_length = (
			max(
				[
					max(
						[len(', '.join(wheel.platform_tags)) for wheel in wheels]
						+ [len('Platforms')]
					),
					len('Platforms'),
				]
			)
			+ 1
		)

		wheel_download_progress = {
			wheel: rich.progress.Progress(
				# rich.progress.SpinnerColumn(),
				'{task.description}',
				rich.progress.BarColumn(
					bar_width=None,
				),
				rich.progress.DownloadColumn(),
				expand=True,
				console=CONSOLE,
			)
			for wheel in wheels
		}
		wheel_download_task: dict[pydeps.BLExtWheel, None | rich.progress.TaskID] = {
			wheel: None for wheel in wheels
		}

		def download_layout():
			table = rich.table.Table(box=None)
			table.add_row(download_progress)
			table.add_row()
			table.add_row(
				f'[bold]{"Name":{max_wheel_project_length}}[/bold]'
				# f' [bold]{"Version":{max_wheel_version_length}}'
				f' [italic]{"Platforms":{max_wheel_version_length}}[/italic]'
			)
			for wheel in sorted(
				wheel_download_progress, key=lambda wheel: wheel.filename
			):
				# table.add_row(
				# f'{wheel.project:{max_wheel_project_length}}'
				# f' {wheel.version:{max_wheel_version_length}}'
				# f' [italic]{", ".join(wheel.platform_tags)}[/italic]'
				# )
				table.add_row(wheel_download_progress[wheel])
			return table

		with rich.live.Live(
			download_layout(),
			console=CONSOLE,
			transient=True,
			refresh_per_second=30,
			screen=False,
		) as live:
			wheels_changed = blext_spec.wheels_graph.download_wheels(
				path_wheels=path_wheels,
				no_prompt=False,
				cb_start_wheel_download=lambda wheel, path_wheel: [
					wheel_download_task.update(
						{
							wheel: wheel_download_progress[wheel].add_task(
								(
									f'{wheel.project:{max_wheel_project_length}}'
									# f' {wheel.version:{max_wheel_version_length}}'
									f' [italic]{", ".join(wheel.platform_tags):{max_wheel_tags_length}}[/italic]'
								),
								total=int(wheel.size) if wheel.size is not None else 0,
							)
						}
					)
				],
				cb_update_wheel_download=lambda wheel, path_wheel, advance: [
					wheel_download_progress[wheel].advance(
						wheel_download_task[wheel],
						advance=advance,
					),
					download_progress.advance(download_task, advance),
					live.update(download_layout()),
				],
				cb_finish_wheel_download=lambda wheel, path_wheel: [
					wheel_download_task.pop(wheel),
					wheel_download_progress.pop(wheel),
					live.update(download_layout()),
				],
			)
			download_progress.stop_task(download_task)

		if wheels_changed:
			CONSOLE.print(f'Downloaded [bold]{len(wheels)} wheels[/bold]')
		else:
			CONSOLE.print(
				f'Found [bold]{len(blext_spec.wheels_graph.wheels)} wheels[/bold] in wheel cache'
			)

		####################
		# - Pre-Pack the Blender Extension
		####################
		path_zip = (
			paths.path_build(blext_spec) / blext_spec.packed_zip_filename
			if output is None
			else output
		)
		if wheels_changed:
			## TODO: More robust detection of whether to re-prepack.
			prepack_progress = rich.progress.Progress(
				rich.progress.SpinnerColumn(),
				'{task.description}',
				rich.progress.BarColumn(
					bar_width=None,
				),
				rich.progress.DownloadColumn(),
				expand=True,
				console=CONSOLE,
			)
			prepack_task = prepack_progress.add_task(
				'Packing',
				total=int(blext_spec.wheels_graph.total_size_bytes),
			)

			wheels_to_write = set(blext_spec.wheels_graph.wheels)
			max_wheel_project_length = (
				max([max(len(wheel.project) for wheel in wheels_to_write), len('Name')])
				+ 1
			)
			max_wheel_byte_size_length = (
				max(
					[
						max(
							len(wheel.size.human_readable())
							if wheel.size is not None
							else 1
							for wheel in wheels_to_write
						),
						len('Size'),
					]
				)
				+ 1
			)
			max_wheel_version_length = (
				max(
					[
						max(len(wheel.version) for wheel in wheels_to_write),
						len('Version'),
					]
				)
				+ 1
			)

			def layout():
				table = rich.table.Table(box=None)
				table.add_row(prepack_progress)
				table.add_row(
					f'[bold]{"Name":{max_wheel_project_length}}[/bold]'
					f' [bold]{"Version":{max_wheel_version_length}}'
					f' [bold]{"Size":{max_wheel_byte_size_length}}'
					f' [italic]{"Platforms":{max_wheel_version_length}}[/italic]'
				)
				for i, wheel in enumerate(
					sorted(wheels_to_write, key=lambda wheel: wheel.filename)
				):
					table.add_row(
						('[green]' if i == 0 else '')
						+ f'{wheel.project:{max_wheel_project_length}}'
						f' {wheel.version:{max_wheel_version_length}}'
						f' {wheel.size.human_readable():{max_wheel_byte_size_length}}'
						f' [italic]{", ".join(wheel.platform_tags)}[/italic]'
					)
				return table

			with rich.live.Live(
				layout(),
				console=CONSOLE,
				transient=True,
				refresh_per_second=10,
			) as live:
				pack.prepack_extension_wheels(
					blext_spec,
					cb_pre_wheel_write=lambda wheel, path_wheel: None,
					cb_post_wheel_write=lambda wheel, path_wheel: [
						prepack_progress.advance(
							prepack_task,
							advance=int(wheel.size) if wheel.size is not None else 0,
						),
						wheels_to_write.remove(wheel),
						live.update(layout()),
					],
				)
			CONSOLE.print(
				f'Packed [bold]{len(blext_spec.wheels_graph.wheels)} wheels[/bold]'
			)
		else:
			CONSOLE.print(
				f'Found [bold]{len(blext_spec.wheels_graph.wheels)} packed wheels[/bold] in packing cache'
			)

		####################
		# - Pack the Blender Extension
		####################
		pack_progress = rich.progress.Progress(
			rich.progress.SpinnerColumn(),
			'Packing [bold]' + blext_spec.id + '[/bold]: {task.description}',
			expand=False,
			console=CONSOLE,
		)
		pack_task = pack_progress.add_task('Packing')
		with rich.live.Live(
			pack_progress,
			console=CONSOLE,
			transient=True,
			refresh_per_second=10,
		) as live:
			pack.pack_bl_extension(
				blext_spec,
				overwrite=True,
				path_zip=path_zip,
				cb_update_status=lambda status: [
					pack_progress.update(pack_task, description=status)
				],
			)

		CONSOLE.print()
		CONSOLE.print(f'Built extension [bold]{blext_spec.id}[/bold]:')
		CONSOLE.print(path_zip)

	####################
	# - Validate Extension
	####################
	# with exc.handle(exc.pretty, ValueError):
	# blender_exe = finders.find_blender_exe()

	### TODO: Dedicated functions so we can reuse this thing
	# CONSOLE.print()
	# CONSOLE.rule('[bold green]Extension Validation')
	# CONSOLE.print('[italic]$ blender --factory-startup --command extension validate')
	# CONSOLE.print()
	# CONSOLE.rule(characters='--', style='gray')

	# path_zip = paths.path_build(blext_spec) / blext_spec.packed_zip_filename
	# bl_process = subprocess.Popen(
	# [
	# blender_exe,
	# '--factory-startup',  ## Temporarily Disable All Addons
	# '--command',  ## Validate an Extension
	# 'extension',
	# 'validate',
	# str(path_zip),
	# ],
	# bufsize=0,  ## TODO: Check if -1 is OK
	# env=os.environ,
	# stdout=sys.stdout,
	# stderr=sys.stderr,
	# )
	# return_code = bl_process.wait()

	# CONSOLE.rule(characters='--', style='gray')
	# CONSOLE.print()
	# if return_code == 0:
	# CONSOLE.print('[✔] Blender Extension Validation Succeeded')
	# else:
	# with exc.handle(exc.pretty, ValueError):
	# msgs = [
	# 'Blender failed to validate the packed extension. For more information, see the validation logs (above).',
	# ]
	# raise ValueError(*msgs)
