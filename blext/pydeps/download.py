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

import concurrent.futures
import functools
import sys
import typing as typ
import urllib.error
import urllib.request
from pathlib import Path

from .pydep_wheel import PyDepWheel

if typ.TYPE_CHECKING:
	import collections.abc


####################
# - Constants
####################
DOWNLOAD_THREADS = 32768
DOWNLOAD_CHUNK_BYTES = 32768

SIGNAL_ABORT: bool = False


####################
# - PyDepWheel Download
####################
def download_wheel(
	wheel_url: str,
	wheel_path: Path,
	*,
	wheel: PyDepWheel,
	cb_update_wheel_download: typ.Callable[
		[PyDepWheel, Path, int], list[None] | None
	] = lambda *_: None,  # pyright: ignore[reportUnknownLambdaType]
	cb_finish_wheel_download: typ.Callable[
		[PyDepWheel, Path], list[None] | None
	] = lambda *_: None,  # pyright: ignore[reportUnknownLambdaType]
) -> None:
	"""Download a Python wheel.

	Notes:
		This function is designed to be run in a background thread.

	Parameters:
		wheel_url: URL to download the wheel from.
		wheel_path: Path to download the wheel to.
		wheel: The wheel spec to be downloaded.
		cb_update_wheel_download: Callback to trigger whenever more data has been downloaded.
		cb_finish_wheel_download: Callback to trigger whenever a wheel has finished downloading.
	"""
	with (
		urllib.request.urlopen(wheel_url, timeout=10) as www_wheel,  # pyright: ignore[reportAny]
		wheel_path.open('wb') as f_wheel,
	):
		raw_data_iterator: collections.abc.Iterator[bytes] = iter(
			functools.partial(
				www_wheel.read,  # pyright: ignore[reportAny]
				DOWNLOAD_CHUNK_BYTES,
			),
			b'',
		)
		for raw_data in raw_data_iterator:
			if SIGNAL_ABORT:
				wheel_path.unlink()
				return

			_ = f_wheel.write(raw_data)
			_ = cb_update_wheel_download(wheel, wheel_path, len(raw_data))

	if not wheel.is_download_valid(wheel_path):
		wheel_path.unlink()
		msg = f'Hash of downloaded wheel at path {wheel_path} did not match expected hash: {wheel.hash}'
		raise ValueError(msg)

	_ = cb_finish_wheel_download(wheel, wheel_path)


def download_wheels(
	wheels: frozenset[PyDepWheel],
	*,
	path_wheels: Path,
	cb_start_wheel_download: typ.Callable[
		[PyDepWheel, Path], typ.Any
	] = lambda *_: None,  # pyright: ignore[reportUnknownLambdaType]
	cb_update_wheel_download: typ.Callable[
		[PyDepWheel, Path, int], typ.Any
	] = lambda *_: None,  # pyright: ignore[reportUnknownLambdaType]
	cb_finish_wheel_download: typ.Callable[
		[PyDepWheel, Path], typ.Any
	] = lambda *_: None,  # pyright: ignore[reportUnknownLambdaType]
) -> None:
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
	"""
	global SIGNAL_ABORT  # noqa: PLW0603

	path_wheels = path_wheels.resolve()
	wheel_paths_current = frozenset(
		{path_wheel.resolve() for path_wheel in path_wheels.rglob('*.whl')}
	)

	# Compute PyDepWheels to Download
	## - Missing: Will be downloaded.
	## - Superfluous: Will be deleted.
	wheels_to_download = {
		path_wheels / wheel.filename: wheel
		for wheel in wheels
		if path_wheels / wheel.filename not in wheel_paths_current
		and wheel.url is not None
	}

	# Download Missing PyDepWheels
	if wheels_to_download:
		with concurrent.futures.ThreadPoolExecutor(
			max_workers=DOWNLOAD_THREADS
		) as pool:
			futures: set[concurrent.futures.Future[None]] = set()
			for path_wheel, wheel in sorted(
				wheels_to_download.items(),
				key=lambda el: el[1].filename,
			):
				cb_start_wheel_download(wheel, path_wheel)
				futures.add(
					pool.submit(
						download_wheel,
						str(wheel.url),
						path_wheel,
						wheel=wheel,
						cb_update_wheel_download=cb_update_wheel_download,
						cb_finish_wheel_download=cb_finish_wheel_download,
					)
				)

			try:
				for future in concurrent.futures.as_completed(futures):
					try:
						future.result()
					except (
						urllib.error.URLError,
						urllib.error.HTTPError,
						urllib.error.ContentTooShortError,
					) as ex:
						SIGNAL_ABORT = True  # pyright: ignore[reportConstantRedefinition]
						pool.shutdown(wait=True, cancel_futures=True)

						SIGNAL_ABORT = False  # pyright: ignore[reportConstantRedefinition]
						msg = (
							'A wheel download aborted with the following message: {ex}'
						)
						raise ValueError(msg) from ex

			except KeyboardInterrupt:
				SIGNAL_ABORT = True  # pyright: ignore[reportConstantRedefinition]
				pool.shutdown(wait=True, cancel_futures=True)

				SIGNAL_ABORT = False  # pyright: ignore[reportConstantRedefinition]
				sys.exit(1)
