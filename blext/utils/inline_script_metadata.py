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

"""Defines the `BLExtSpec` model."""

import re
import tomllib
import typing as typ

INLINE_METADATA_BLOCK_NAME = 'script'
INLINE_SCRIPT_METADATA_REGEX = (
	r'(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$'
)


def parse_inline_script_metadata(
	*,
	block_name: str = INLINE_METADATA_BLOCK_NAME,
	py_source_code: str,
) -> dict[str, typ.Any] | None:
	"""Parse inline script metadata from Python source code.

	Parameters:
		block_name: The name of the metadata block type to parse from the source code's header.
			For instance, setting this to `script` will parse blocks starting with `# /// script` (and ending with `# ///`).
		py_source_code: The Python source code to parse for inline script metadata.
			The script must start with a `# /// TYPE` metadata blocks.

	Returns:
		A dictionary of inline script metadata, in a format equivalent to that of `pyproject.toml`, if such metadata could be parsed.

		Otherwise the return value is `None`.

	References:
		PyPa on Inline Script Metadata: <https://packaging.python.org/en/latest/specifications/inline-script-metadata>
	"""
	matches = [
		match
		for match in re.finditer(INLINE_SCRIPT_METADATA_REGEX, py_source_code)
		if match.group('type') == block_name
	]

	if len(matches) == 1:
		return tomllib.loads(
			''.join(
				line[2:] if line.startswith('# ') else line[1:]
				for line in matches[0].group('content').splitlines(keepends=True)
			)
		)

	if len(matches) > 1:
		msg = f'Multiple `{block_name}` blocks of inline script metadata were found.'
		raise ValueError(msg)

	return None
