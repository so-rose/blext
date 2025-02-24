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
import signal
import sys
import threading
import typing as typ
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen

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
# EVENT_DONE = threading.Event()


# def handle_sigint(signum, frame):
# EVENT_DONE.set()
#
#
# signal.signal(signal.SIGINT, handle_sigint)


####################
# - Wheel Download
####################
def download_wheel(
	wheel_url: str,
	wheel_path: Path,
	*,
	wheel: BLExtWheel,
	cb_update_wheel_download: typ.Callable[
		[BLExtWheel, Path, int], list[None] | None
	] = lambda *_: None,
	cb_finish_wheel_download: typ.Callable[
		[BLExtWheel, Path], list[None] | None
	] = lambda *_: None,
) -> None:
	response = urlopen(wheel_url)
	with wheel_path.open('wb') as f_wheel:
		for raw_data in iter(functools.partial(response.read, 32768), b''):
			f_wheel.write(raw_data)
			cb_update_wheel_download(wheel, wheel_path, len(raw_data))

			# if EVENT_DONE.is_set():
			# wheel_path.unlink()
			# return

	cb_finish_wheel_download(wheel, wheel_path)


def download_wheels(
	wheels: frozenset[BLExtWheel],
	*,
	path_wheels: Path,
	no_prompt: bool = False,
	cb_start_wheel_download: typ.Callable[
		[BLExtWheel, Path], typ.Any
	] = lambda *_: None,
	cb_update_wheel_download: typ.Callable[
		[BLExtWheel, Path, int], typ.Any
	] = lambda *_: None,
	cb_finish_wheel_download: typ.Callable[
		[BLExtWheel, Path], typ.Any
	] = lambda *_: None,
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
	## TODO:
	# if wheel_paths_to_delete:
	# for path_wheel in wheel_paths_to_delete:
	# if path_wheel.is_file() and path_wheel.name.endswith('.whl'):
	# path_wheel.unlink()
	# else:
	# msg = f"While deleting superfluous wheels, a wheel path was computed that doesn't point to a valid .whl wheel: {path_wheel}"
	# raise RuntimeError(msg)

	# Download Missing Wheels
	if wheels_to_download:
		with ThreadPoolExecutor(max_workers=8) as pool:
			for path_wheel, wheel in sorted(
				wheels_to_download.items(),
				key=lambda el: el[1].filename,
			):
				cb_start_wheel_download(wheel, path_wheel)
				pool.submit(
					download_wheel,
					str(wheel.url),
					path_wheel,
					wheel=wheel,
					cb_update_wheel_download=cb_update_wheel_download,
					cb_finish_wheel_download=cb_finish_wheel_download,
				)

		# TODO: Check hashes of all downloaded wheels.

	return bool(len(wheels_to_download) > 0 or len(wheel_paths_to_delete) > 0)
