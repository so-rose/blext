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

import contextlib
import sys
from pathlib import Path

import rich
import rich.markdown
import rich.padding
import pydantic as pyd


def sys_exit_1():
	sys.exit(1)


@contextlib.contextmanager
def handle(
	ex_handler,
	*exceptions,
	after_ex=sys_exit_1,
):
	try:
		yield
	except exceptions as ex:
		ex_handler(ex)
		after_ex()


####################
# - Exception Handlers
####################
def pretty(ex: Exception, show_filename_lineno: bool = False) -> None:
	# Parse ValidationError
	if isinstance(ex, pyd.ValidationError):
		model_name = ex.title
		ex_name = f'ValidationError{"s" if ex.error_count() > 1 else ""}'

		ex = ValueError(
			*[
				f'{model_name}.'
				+ ', '.join([str(el) for el in err['loc']])
				+ '='
				+ str(err['input'])
				+ ': '
				+ err['msg']
				for err in ex.errors()
			]
		)
	else:
		ex_name = ex.__class__.__name__

	# Parse Filename and Line#
	if show_filename_lineno:
		_, exc_obj, exc_tb = sys.exc_info()
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
		rich.padding.Padding(rich.markdown.Markdown(arg), pad=(0, 0, 0, 4))
		for arg in ex.args
	]

	# Present
	rich.print(
		f'[bold red]{ex_name}[/bold red]',
		info,
		*messages,
		sep='',
	)
