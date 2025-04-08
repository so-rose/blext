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

"""Implements a UI that reports the download progress of Python wheels."""

import collections.abc
import contextlib
import functools
import typing as typ
from pathlib import Path

import pydantic as pyd
import rich.console
import rich.live
import rich.progress
import rich.table

from blext import pydeps


####################
# - Structs
####################
class CallbacksDownloadWheel(pyd.BaseModel):
	"""Callbacks to trigger in the process of downloading wheels.

	Notes:
		- All that a download agent has to ensure, is to allow the user to specify
		equivalent callbacks to these.
		- The callback return values are never used for any purpose.

	Attributes:
		cb_start_wheel_download: Called as a wheel is starting to be downloaded.
			Called with the wheel, and with its download path.
			_Always called before `cb_update_wheel_download` for a wheel._
		cb_update_wheel_download: Called when an actively downloading wheel
			Called with the wheel, and its download path, and newly downloaded bytes.
			_Always called after `cb_start_wheel_download` for a wheel._
		cb_finish_wheel_download: Called when an actively downloading wheel
			_No other callbacks are called for a wheel after this._

	See Also:
		- `blext.pydeps.network.download_wheels`: Download agent that uses equivalent callbacks.
		- `blext.ui.ui_download_wheels`: Context manager that provides this object.
	"""

	cb_start_wheel_download: typ.Callable[[pydeps.PyDepWheel, Path], typ.Any]
	cb_update_wheel_download: typ.Callable[[pydeps.PyDepWheel, Path, int], typ.Any]
	cb_finish_wheel_download: typ.Callable[[pydeps.PyDepWheel, Path], typ.Any]


####################
# - UI
####################
@contextlib.contextmanager
def ui_download_wheels(
	wheels_to_download: frozenset[pydeps.PyDepWheel],
	*,
	console: rich.console.Console,
	fps: int = 24,
) -> collections.abc.Generator[CallbacksDownloadWheel, None, None]:
	"""Context manager creating a terminal UI to communicate wheel downloading.

	Notes:
		Yields callbacks to call during the download progress, in order for the UI to update correctly.

	Parameters:
		wheels_to_download: Set of wheels to download.
		console: `rich` console to print the UI to.
		fps: Number of updates to the terminal, per second.


	See Also:
		`blext.ui.download_wheels.CallbacksDownloadWheel`: For more on when to call each callback.
	"""
	bytes_to_download = sum(int(wheel.size) for wheel in wheels_to_download)

	####################
	# - Progress: Overall Download
	####################
	progress_download_all = rich.progress.Progress(
		rich.progress.SpinnerColumn(),
		'{task.description}',
		rich.progress.BarColumn(
			bar_width=None,
		),
		rich.progress.DownloadColumn(),
		expand=True,
		console=console,
	)
	task_download_all = progress_download_all.add_task(
		'Downloading',
		total=bytes_to_download,
		start=True,
	)

	####################
	# - Progress: Individual Wheels
	####################
	progress_download_wheels = {
		wheel: rich.progress.Progress(
			rich.progress.BarColumn(
				bar_width=None,
			),
			rich.progress.DownloadColumn(),
			expand=True,
			console=console,
		)
		for wheel in wheels_to_download
	}
	task_download_wheels: dict[pydeps.PyDepWheel, None | rich.progress.TaskID] = (
		dict.fromkeys(wheels_to_download)
	)

	####################
	# - Callbacks
	####################
	def cb_start_wheel_download(
		wheel: pydeps.PyDepWheel,
		_: Path,
	) -> None:
		task_download_wheels.update({
			wheel: progress_download_wheels[wheel].add_task(
				wheel.filename,
				total=int(wheel.size),
			)
		})

	def cb_update_wheel_download(
		wheel: pydeps.PyDepWheel,
		_: Path,
		advance: int,
	) -> None:
		task_download_wheel = task_download_wheels[wheel]
		if task_download_wheel is not None:
			progress_download_all.advance(task_download_all, advance=advance)
			progress_download_wheels[wheel].advance(
				task_download_wheel,
				advance=advance,
			)
		else:
			msg = f'`rich.progress.Task` was not initialized for `{wheel.filename}` - something is very wrong!'
			raise RuntimeError(msg)

	def cb_finish_wheel_download(
		wheel: pydeps.PyDepWheel,
		_: Path,
	) -> None:
		del task_download_wheels[wheel]
		del progress_download_wheels[wheel]

	####################
	# - Layout: Static UI
	####################
	max_wheel_project_length = max([
		*[len(wheel.project) for wheel in wheels_to_download],
		len('Name'),
	])

	def layout() -> rich.console.Group:
		"""Generate a static UI, valid at one moment in time."""
		# Progress (Overall)
		table_overall_progress = rich.table.Table(box=None)
		table_overall_progress.add_row(progress_download_all)
		table_overall_progress.add_row()

		# Progress (by Wheel)
		table_wheel_progress = rich.table.Table(expand=True, box=None)
		table_wheel_progress.add_column(
			'Name',
			header_style='bold',
			justify='left',
			no_wrap=True,
			min_width=max_wheel_project_length - 6,
		)
		table_wheel_progress.add_column(
			'Platforms',
			header_style='bold',
			style='italic',
			justify='left',
			no_wrap=False,
			ratio=2,
		)
		table_wheel_progress.add_column(
			'Progress',
			header_style='bold',
			justify='left',
			no_wrap=True,
			ratio=6,  ## Make this column greedy
		)
		for wheel in sorted(progress_download_wheels, key=lambda wheel: wheel.filename):
			if task_download_wheels[wheel] is not None:
				table_wheel_progress.add_row(
					wheel.project,
					wheel.pretty_bl_platforms,
					progress_download_wheels[wheel],
				)

		return rich.console.Group(
			table_overall_progress,
			table_wheel_progress,
		)

	####################
	# - Live: Dynamic UI
	####################
	with rich.live.Live(
		get_renderable=layout,
		console=console,
		transient=True,
		refresh_per_second=fps,
	):
		yield CallbacksDownloadWheel(
			cb_start_wheel_download=functools.partial(
				cb_start_wheel_download,
			),
			cb_update_wheel_download=functools.partial(
				cb_update_wheel_download,
			),
			cb_finish_wheel_download=functools.partial(
				cb_finish_wheel_download,
			),
		)

	progress_download_all.stop_task(task_download_all)
