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
class CallbacksPrepackExtension(pyd.BaseModel):
	"""Simple callback-storage, for use with `blext.pydeps.network.download_wheels."""

	cb_pre_file_write: typ.Callable[[Path, Path], typ.Any]
	cb_post_file_write: typ.Callable[[Path, Path], typ.Any]


####################
# - UI
####################
@contextlib.contextmanager
def ui_prepack_extension(
	files_to_prepack: dict[Path, Path],
	*,
	console: rich.console.Console,
	fps: int = 30,
) -> collections.abc.Generator[CallbacksPrepackExtension, None, None]:
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
	def cb_pre_file_write(
		path: Path,
		zipfile_path: Path,
		*,
		live: rich.live.Live,
	) -> None:
		pass

	def cb_post_file_write(
		path: Path,
		zipfile_path: Path,
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
			table_wheel_progress.add_row(
				pyd.ByteSize(file_sizes[path]).human_readable(decimal=True),
				str(Path('wheels') / path.name),
				**({'style': 'green'} if i == 0 else {}),
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
