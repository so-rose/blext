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

"""Implements a UI that reports the progress of extension pre-packing."""

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


####################
# - Structs
####################
@typ.runtime_checkable
class PrepackCallback(typ.Protocol):
	"""Callback for use in `CallbacksPrepackExtension`."""

	def __call__(  # pyright: ignore[reportAny]
		self,
		path: Path,
		zipfile_path: Path,
		*,
		live: rich.live.Live,
	) -> typ.Any:
		"""Signature of the callback."""


class CallbacksPrepackExtension(pyd.BaseModel, arbitrary_types_allowed=True):
	"""Callbacks to trigger in the process of pre-packing an extension.

	Notes:
		- All callbacks additionally take a `live=` keyword argument
		- All that a pre-pack agent has to ensure, is to allow the user to specify
		equivalent callbacks to these.
		- The callback return values are never used for any purpose.

	Attributes:
		cb_pre_file_write: Called as a file is about to be pre-packed.
			Called with the host path, and the zipfile path.
			_Always called before `cb_post_file_write` for a file._
		cb_post_file_write: Called after a file has been pre-packed.
			Called with the host path, and the zipfile path.
			_Always called before `cb_post_file_write` for a file._

	See Also:
		- `blext.pack.prepack_extension`: Prepack agent that uses equivalent callbacks.
		- `blext.ui.ui_prepack_extension`: Context manager that provides this object.
	"""

	cb_pre_file_write: PrepackCallback
	cb_post_file_write: PrepackCallback


####################
# - UI
####################
@contextlib.contextmanager
def ui_prepack_extension(
	files_to_prepack: dict[Path, Path],
	*,
	console: rich.console.Console,
) -> collections.abc.Generator[CallbacksPrepackExtension, None, None]:
	"""Context manager creating a terminal UI to communicate extension prepacking progress.

	Parameters:
		files_to_prepack: Files to be prepack.
			Maps an absolute host filesystem path, to a relative zipfile path.
		console: `rich` console to print the UI to.

	Yields:
		Callbacks to call during the download progress, in order for the UI to update correctly.

	See Also:
		`blext.ui.download_wheels.CallbacksDownloadWheel`: For more on when to call each callback.
	"""
	file_sizes = {path: path.stat().st_size for path in files_to_prepack}
	bytes_to_prepack = sum(file_size for file_size in file_sizes.values())

	####################
	# - Progress: Overall Download
	####################
	remaining_files_to_prepack = set(files_to_prepack.keys())
	progress_prepack = rich.progress.Progress(
		rich.progress.SpinnerColumn(),
		'{task.description}',
		rich.progress.BarColumn(
			bar_width=None,
		),
		rich.progress.DownloadColumn(),
		expand=True,
		console=console,
	)
	task_prepack = progress_prepack.add_task(
		'Pre-Packing',
		total=bytes_to_prepack,
		start=True,
	)

	####################
	# - Callbacks
	####################
	def cb_pre_file_write(*_, **__) -> None:  # pyright: ignore[reportUnusedParameter, reportMissingParameterType, reportUnknownParameterType]
		pass

	def cb_post_file_write(
		path: Path,
		_: Path,
		*,
		live: rich.live.Live,
	) -> None:
		progress_prepack.advance(
			task_prepack,
			advance=file_sizes[path],
		)
		remaining_files_to_prepack.remove(path)
		live.refresh()

	####################
	# - Layout: Static UI
	####################
	def layout() -> rich.console.Group:
		"""Generate a static UI, valid at one moment in time."""
		# Progress (Overall)
		table_overall_progress = rich.table.Table(box=None)
		table_overall_progress.add_row(progress_prepack)
		table_overall_progress.add_row()

		# Progress (by Wheel)
		table_wheel_progress = rich.table.Table(expand=True, box=None)
		table_wheel_progress.add_column(
			'Size',
			header_style='bold',
			justify='left',
			no_wrap=True,
		)
		table_wheel_progress.add_column(
			'Packed Path',
			header_style='bold',
			justify='right',
			no_wrap=False,
		)
		for i, path in enumerate(
			sorted(remaining_files_to_prepack, key=lambda path: file_sizes[path])
		):
			style = {'style': 'green'} if i == 0 else {}
			table_wheel_progress.add_row(
				pyd.ByteSize(file_sizes[path]).human_readable(decimal=True),
				str(Path('wheels') / path.name),
				**style,  # pyright: ignore[reportArgumentType]
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
		auto_refresh=False,
	) as live:
		yield CallbacksPrepackExtension(
			cb_pre_file_write=functools.partial(cb_pre_file_write, live=live),
			cb_post_file_write=functools.partial(cb_post_file_write, live=live),
		)

		progress_prepack.stop_task(task_prepack)
