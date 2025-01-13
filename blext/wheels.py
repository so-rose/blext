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

import contextlib
import subprocess
import sys
import time
import tomllib

import pypdl
import rich
import rich.markdown
import rich.progress
import rich.prompt

from . import pack, spec, supported

console = rich.console.Console()

DELAY_DOWNLOAD_PROGRESS = 0.01


####################
# - Wheel Downloader
####################
def desired_wheels(blext_spec: spec.BLExtSpec) -> tuple[set[str], dict[str, str]]:
	"""Deduce the filenames and URLs of the desired wheels."""
	# Run uv Commands
	with contextlib.chdir(blext_spec.path_proj_root):
		# Generate uv.lock
		subprocess.run(
			['uv', 'lock'],
			check=True,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)

		# Retrieve Dependencies
		## - uv must declare which dependencies are NOT dev dependencies.
		uv_tree_str = subprocess.check_output(
			['uv', 'tree', '--no-dev', '--locked'],
			stderr=subprocess.DEVNULL,
		).decode('utf-8')

	# Find or Create uv.lock
	path_uv_lock = blext_spec.path_proj_root / 'uv.lock'
	if not path_uv_lock.is_file():
		msg = f"Couldn't find or create 'uv.lock' in project root '{blext_spec.path_proj_root}'"
		raise ValueError(msg)

	# Parse for All Wheel Filenames
	with path_uv_lock.open('rb') as f:
		uv_lockfile = tomllib.load(f)

	wheel_filename_to_url = {
		wheel['url'].split('/')[-1]: wheel['url']
		for pkg in uv_lockfile['package']
		for wheel in pkg.get('wheels', [])
		if 'wheels' in pkg and pkg['name'] in uv_tree_str
	}
	wheel_filename_to_url = {
		wheel_filename: wheel_url
		for wheel_filename, wheel_url in wheel_filename_to_url.items()
		if any(
			pypa_tag in wheel_filename or 'py3-none-any' in wheel_filename
			for bl_platform, pypa_tags in blext_spec.bl_platform_pypa_tags.items()
			for pypa_tag in pypa_tags
		)
	}

	return (
		set(wheel_filename_to_url.keys()),
		wheel_filename_to_url,
	)


def download_wheels(
	blext_spec: spec.BLExtSpec,
	*,
	bl_platform: supported.BLPlatform,
	no_prompt: bool = False,
) -> None:
	"""Download universal and binary wheels for all platforms defined in `pyproject.toml`.

	Each blender-supported platform requires specifying a valid list of PyPi platform constraints.
	These will be used as an allow-list when deciding which binary wheels may be selected for ex. 'mac'.

	It is recommended to start with the most compatible platform tags, then work one's way up to the newest.
	Depending on how old the compatibility should stretch, one may have to omit / manually compile some wheels.

	There is no exhaustive list of valid platform tags - though this should get you started:
	- https://stackoverflow.com/questions/49672621/what-are-the-valid-values-for-platform-abi-and-implementation-for-pip-do
	- Examine https://pypi.org/project/pillow/#files for some widely-supported tags.

	Args:
		delete_existing_wheels: Whether to delete all wheels already in the directory.
			This doesn't generally require re-downloading; the pip-cache will generally be hit first.
	"""
	# Deduce Current | Desired Wheels
	wheels_current = {path.name for path in blext_spec.path_wheels.rglob('*.whl')}
	wheels_target, wheel_target_urls = desired_wheels(blext_spec)

	# Compute Wheels to Download / Delete
	wheels_to_download = wheels_target - wheels_current
	wheels_to_delete = wheels_current - wheels_target

	# Delete Superfluous Wheels
	if wheels_to_delete:
		console.print()
		console.rule('[bold green]Wheels to Delete')
		console.print(f'[italic]Deleting from: {blext_spec.path_wheels}:')
		console.print(
			rich.markdown.Markdown(
				'\n'.join(
					[f'- {wheel_to_delete}' for wheel_to_delete in wheels_to_delete]
				)
			),
		)
		console.print()

		if not no_prompt:
			if rich.prompt.Confirm.ask('[bold]OK to delete?'):
				for wheel_filename in wheels_to_delete:
					wheel_path = blext_spec.path_wheels / wheel_filename
					if wheel_path.is_file():
						wheel_path.unlink()
					else:
						msg = f"While deleting superfluous wheels, a wheel path was computed that doesn't point to a valid file: {wheel_path}"
						raise RuntimeError(msg)
			else:
				sys.exit(1)

	# Download Missing Wheels
	if wheels_to_download:
		console.print()
		console.rule('[bold green]Wheels to Download')
		console.print(f'[italic]Downloading to: {blext_spec.path_wheels}')
		console.print(
			rich.markdown.Markdown(
				'\n'.join(
					[
						f'- {wheel_to_download}'
						for wheel_to_download in wheels_to_download
					]
				)
			),
		)
		console.print()

		# Start Download
		dl = pypdl.Pypdl(
			max_concurrent=8,
			allow_reuse=False,
		)
		future = dl.start(
			tasks=[
				{
					'url': wheel_url,
					'file_path': str(blext_spec.path_wheels / wheel_filename),
				}
				for wheel_filename, wheel_url in wheel_target_urls.items()
			],
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
			while dl.progress < 99:  # noqa: PLR2004
				progress.update(task, completed=dl.progress)
				time.sleep(DELAY_DOWNLOAD_PROGRESS)

			# Stop the Download @ 99%
			## - Essentially, we must wait on the future from the started download.
			## - This also merges the downloaded segments and cleans up.
			future.result()

			# Finalize Progress Bar to 100%
			progress.update(task, completed=100)

	# Prepack ZIP
	if wheels_to_delete or wheels_to_download:
		pack.prepack_bl_extension(blext_spec)
