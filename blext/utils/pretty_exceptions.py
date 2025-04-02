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

import functools
import operator
import types

import pydantic as pyd
import rich
import rich.markdown
import rich.theme
import rich.traceback

ERROR_CONSOLE = rich.console.Console(
	tab_size=2,
	theme=rich.theme.Theme(
		styles={
			'markdown.code': 'italic dim',
			'cyan': 'green',
		}
	),
)


####################
# - Exception Handler
####################
def exception_hook(
	ex_type: type[BaseException],
	ex: BaseException,
	traceback: types.TracebackType | None,
) -> None:
	"""Prettifies exceptions incl. allowing the use of markdown in messages.

	Parameters:
		ex_type: Type of the exception that was raised.
		ex: The exception that was raised.
		traceback: The reported traceback.

	"""
	ex_name = ex.__class__.__name__

	if isinstance(ex, pyd.ValidationError):
		ex_name = f'ValidationError{"s" if ex.error_count() > 1 else ""}'
		messages = [
			f'`{ex.title}`: {ex.error_count()} errors were encountered while parsing inputs.',
			*functools.reduce(
				operator.add,
				[
					[
						f'> `{ex.title}.{".".join(str(el) for el in err["loc"])}`',
						f'> - **Input**: `{err["input"]}`',
						f'> - **Error**: {err["msg"]}.',
						f'> - **Context**: `{err["ctx"]}`'  # pyright: ignore[reportTypedDictNotRequiredAccess]
						if err.get('ctx') is not None
						else '>',
						'>',
						f'> **Error Ref**: <{err.get("url")}>'
						if err.get('url') is not None
						else '>',
						'',
					]
					for err in ex.errors()
				],
			),
		]

	elif isinstance(ex, ValueError | NotImplementedError):
		messages = [str(arg) for arg in ex.args]  # pyright: ignore[reportAny]

	else:
		rich_traceback = rich.traceback.Traceback.from_exception(
			ex_type,
			ex,
			traceback,
			width=ERROR_CONSOLE.width,
			word_wrap=True,
		)
		ERROR_CONSOLE.print(rich_traceback)
		return

	md_messages = rich.markdown.Markdown('\n'.join(messages))

	# Present
	ERROR_CONSOLE.print(
		'\n',
		f'[bold red]{ex_name}[/bold red]',
		'\n',
		md_messages,
		sep='',
	)
