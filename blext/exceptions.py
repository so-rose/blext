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

"""Exception handling for enhancing the end-user experience of dealing with errors."""

import collections.abc
import contextlib
import sys
import typing as typ
from pathlib import Path

import pydantic as pyd
import rich
import rich.markdown
import rich.padding


@contextlib.contextmanager
def handle(
	ex_handler: typ.Callable[[Exception], None],
	*exceptions: type[Exception],
	after_ex: typ.Callable[[], None] = lambda: sys.exit(1),
) -> collections.abc.Generator[None, None, None]:
	"""Handle exceptions thrown in a block with custom logic.

	Useful for transforming the style or behavior of what throwing an exception should do.
	In particular, it is generally desirable to have shorter, more user-friendly errors in
	CLI applications, while simultaneously allowing normal extension logic to be used internally.

	Parameters:
		ex_handler: The exception handler, to which the exception is passed as the only argument.
		exceptions: The exception types to handle using ex_handler.
			Use ex. `ValueError` exception types here directly.
		after_ex: Something
			By default, exit the program with exit-code 1.

	Returns:
		A generator, for use in a `with` statement.
		Anything inside the `with` statement will have the defined subset of its
		exceptions handled with the given method.

	Examples:
		```python
		with handle(pretty, ValueError):
			raise ValueError("Pretty-Printed Message")
		```
	"""
	try:
		yield
	except exceptions as ex:
		ex_handler(ex)
		after_ex()


####################
# - Exception Handlers
####################
def pretty(ex: Exception, show_filename_lineno: bool = False) -> None:
	"""Print an exception in a more stylish, end-user oriented fashion.

	Designed for use with `handle`.

	Parameters:
		ex: The exception to transform and print.
		show_filename_lineno: Whether to include the filename and line number that caused the error.
	"""
	# Parse ValidationError
	if isinstance(ex, pyd.ValidationError):
		model_name = ex.title
		ex_name = f'ValidationError{"s" if ex.error_count() > 1 else ""}'

		ex = ValueError(
			*[
				f'{model_name}.'
				+ ', '.join([str(el) for el in err['loc']])
				+ '='
				+ str(err['input'])  # pyright: ignore[reportAny]
				+ ': '
				+ err['msg']
				for err in ex.errors()
			]
		)
	else:
		ex_name = ex.__class__.__name__

	# Parse Filename and Line#
	if show_filename_lineno:
		_, _, exc_tb = sys.exc_info()
		filename = (
			Path(exc_tb.tb_frame.f_code.co_filename).name
			if exc_tb is not None
			else None
		)
		lineno = exc_tb.tb_lineno if exc_tb is not None else None
		info = f' ({filename}|{lineno}):' if exc_tb is not None else ':'
	else:
		info = ':'

	# Format Message Tuple
	messages = [
		rich.padding.Padding(
			rich.markdown.Markdown(arg),  # pyright: ignore[reportAny]
			pad=(0, 0, 0, 4),
		)
		for arg in ex.args  # pyright: ignore[reportAny]
	]

	# Present
	rich.print(
		f'[bold red]{ex_name}[/bold red]',
		info,
		*messages,
		sep='',
	)
