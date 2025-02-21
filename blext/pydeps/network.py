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

import sys
import time
from pathlib import Path

import pypdl
import pypdl.utils
import rich
import rich.markdown
import rich.progress
import rich.prompt

from .wheel import BLExtWheel

CONSOLE = rich.console.Console()

DELAY_DOWNLOAD_PROGRESS = 0.01
DOWNLOAD_DONE_THRESHOLD = 99


####################
# - Wheel Download
####################


def download_wheels(
	wheels: frozenset[BLExtWheel],
	*,
	path_wheels: Path,
	no_prompt: bool = False,
) -> bool:
	"""Download universal and binary wheels for all platforms defined in `pyproject.toml`.

	Each blender-supported platform requires specifying a valid list of PyPi platform constraints.
	These will be used as an allow-list when deciding which binary wheels may be selected for ex. 'mac'.

	It is recommended to start with the most compatible platform tags, then work one's way up to the newest.
	Depending on how old the compatibility should stretch, one may have to omit / manually compile some wheels.

	There is no exhaustive list of valid platform tags - though this should get you started:
	- https://stackoverflow.com/questions/49672621/what-are-the-valid-values-for-platform-abi-and-implementation-for-pip-do
	- Examine https://pypi.org/project/pillow/#files for some widely-supported tags.

	Parameters:
		blext_spec: The extension specification to pack the zip file base on.
		bl_platform: The Blender platform to get wheels for.
		no_prompt: Don't protect wheel deletion with an interactive prompt.
	"""
	path_wheels = path_wheels.resolve()
	wheel_paths_current = frozenset(
		{path_wheel.resolve() for path_wheel in path_wheels.rglob('*.whl')}
	)

	# Compute Wheel Diff
	## - Missing: Will be downloaded.
	## - Superfluous: Will be deleted.
	wheels_to_download = {
		path_wheels / wheel.filename: wheel
		for wheel in wheels
		if path_wheels / wheel.filename not in wheel_paths_current
		and wheel.url is not None
	}
	wheel_paths_to_delete = wheel_paths_current - frozenset(
		{path_wheels / wheel.filename for wheel in wheels}
	)
	## TODO: Check hash of existing wheels.

	# Delete Superfluous Wheels
	if wheel_paths_to_delete:
		CONSOLE.print()
		CONSOLE.rule('[bold green]Wheels to Delete')
		CONSOLE.print(f'[italic]Deleting from: {path_wheels}:')
		CONSOLE.print(
			rich.markdown.Markdown(
				'\n'.join(
					[
						f'- {wheel_path_to_delete.relative_to(path_wheels)}'
						for wheel_path_to_delete in wheel_paths_to_delete
					]
				)
			),
		)
		CONSOLE.print()

		if not no_prompt:
			if rich.prompt.Confirm.ask('[bold]OK to delete?'):
				for path_wheel in wheel_paths_to_delete:
					if path_wheel.is_file() and path_wheel.name.endswith('.whl'):
						path_wheel.unlink()
					else:
						msg = f"While deleting superfluous wheels, a wheel path was computed that doesn't point to a valid .whl wheel: {path_wheel}"
						raise RuntimeError(msg)
			else:
				CONSOLE.print('[italic]Aborting...[/italic]')
				sys.exit(1)

	# Download Missing Wheels
	if wheels_to_download:
		CONSOLE.print()
		CONSOLE.rule('[bold green]Wheels to Download')
		CONSOLE.print(f'[italic]Downloading to: {path_wheels}')
		CONSOLE.print(
			rich.markdown.Markdown(
				'\n'.join(
					[
						f'- {wheel_path_to_download.relative_to(path_wheels)}'
						for wheel_path_to_download in wheels_to_download
					]
				)
			),
		)
		CONSOLE.print()

		# Start Download
		dl_tasks = [
			{
				'url': str(wheel.url),
				'file_path': str(path_wheel),
			}
			for path_wheel, wheel in wheels_to_download.items()
		]
		if dl_tasks:
			dl = pypdl.Pypdl(  # pyright: ignore[reportPrivateLocalImportUsage]
				max_concurrent=8,
				allow_reuse=False,
			)
			dl_promise: pypdl.utils.EFuture = dl.start(  # pyright: ignore[reportUnknownMemberType, reportAssignmentType]
				tasks=dl_tasks,
				retries=3,
				display=False,
				block=False,
			)

			# Monitor Download w/Progress Bar
			with rich.progress.Progress() as progress:
				task = progress.add_task('Downloading...', total=100)

			# Wait for Download to Start
			while dl.progress is None:
				time.sleep(DELAY_DOWNLOAD_PROGRESS)

			# Monitor Download
			## - 99% seems to be the maximum value.
			while dl.progress < DOWNLOAD_DONE_THRESHOLD:
				progress.update(task, completed=dl.progress)
				time.sleep(DELAY_DOWNLOAD_PROGRESS)

			# Stop the Download @ 99%
			## - Essentially, we must wait on the future from the started download.
			## - This also merges the downloaded segments and cleans up.
			_ = dl_promise.result()

			# Finalize Progress Bar to 100%
			progress.update(task, completed=100)

		## TODO: Reimplement for locally built wheels w/Copy
		# copy_tasks = [
		# {
		# 'from': wheel_path,
		# 'to': blext_spec.path_wheels / wheel_filename,
		# }
		# for wheel_filename, wheel_path in wheel_target_urls.items()
		# if wheel_filename in wheels_to_download and isinstance(wheel_path, Path)
		# ]
		# for copy_task in copy_tasks:
		# shutil.copyfile(str(copy_task['from']), str(copy_task['to']))

	return bool(len(wheels_to_download) > 0 or len(wheel_paths_to_delete) > 0)
