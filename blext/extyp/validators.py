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

"""Functions that help validate."""

import os.path
import re


####################
# - Manifest Validation
####################
def no_dunder_in_string(s: str) -> bool:
	"""Whether `__` is in `s`."""
	return '__' not in s


def no_str_startswith_underscore(s: str) -> bool:
	"""Whether `s` starts with `_`."""
	return not s.startswith('_')


def no_str_endswith_underscore(s: str) -> bool:
	"""Whether `s` ends with `_`."""
	return not s.endswith('_')


_BL_SEMVER_PATTERN: re.Pattern[str] = re.compile(
	r'^'  # pyright: ignore[reportImplicitStringConcatenation]
	r'(?P<major>0|[1-9]\d*)\.'
	r'(?P<minor>0|[1-9]\d*)\.'
	r'(?P<patch>0|[1-9]\d*)'
	r'(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
	r'(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
)


def is_valid_bl_semver(s: str) -> bool:
	"""Whether `s` is valid semver, as defined by Blender."""
	return _BL_SEMVER_PATTERN.search(s) is not None


def is_str_strip_not_empty(s: str) -> bool:
	"""Whether `s.strip()` is an empty string."""
	return bool(s.strip())


def is_str_strip_a_noop(s: str) -> bool:
	"""Whether `s.strip()` is equal to `s`."""
	return s == s.strip()


_BL_CONTROL_CHARS: re.Pattern[str] = re.compile(r'[\x00-\x1f\x7f-\x9f]')


def str_has_no_bl_control_chars(s: str) -> bool:
	"""Whether `s` contains any control characters, as defined by Blender."""
	return len(list(_BL_CONTROL_CHARS.finditer(s))) == 0


def last_char_is_alphanum_or_closes_bracket(s: str) -> bool:
	"""Whether the last character of `s` is either alphanumeric, or ends with `)`, `]`, or `}`."""
	if s:
		return s[-1].isalnum() or s[-1] in [')', ']', '}']
	return False


def all_version_numbers_are_digits(s: str) -> bool:
	"""Whether `s`, a version, has all-digit numbers."""
	return all(number_str.isdigit() for number_str in s.split('.'))


def blender_version_is_gt_4_2(s: str) -> bool:
	"""Whether `s`, a Blender version, is greater than `4.2`."""
	version_tuple = tuple(int(number_str) for number_str in s.split('.'))
	return (version_tuple[0] == 4 and version_tuple[1] >= 2) or version_tuple[0] > 4  # noqa: PLR2004


def is_copyright_year_valid(s: str) -> bool:
	"""Whether `s`, a copyright statement, has a valid copyright year."""
	year = s.partition(' ')[0]
	year_split = year.partition('-')

	if year_split[1]:
		return year_split[0].isdigit() and year_split[2].isdigit()
	return year.isdigit()


def is_copyright_name_valid(s: str) -> bool:
	"""Whether `s`, a copyright statement, has a valid copyright name."""
	_, name = s.partition(' ')[0::2]

	return bool(name.strip())


def wheel_filename_has_no_double_quotes(s: str) -> bool:
	"""Whether `s`, a wheel filename, contains double quotes."""
	return r'"' not in s


def wheel_filename_has_no_backward_slashes(s: str) -> bool:
	"""Whether the input wheel filename string has any backward slash characters.

	Notes:
		Equivalent to a [`blender_ext.py` snippet](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1729).

		It should be noted that the error message in this snippet claims to be checking for "forward slashes", when in fact it checks for backslash characters.
	"""
	return '\\' not in s


def lowercase_wheel_filename_endswith_whl(s: str) -> bool:
	"""Whether `s`, a wheel filename, ends with `whl` or `WHL`."""
	return os.path.basename(s).lower().endswith('whl')  # noqa: PTH119


def wheel_filename_has_valid_number_of_dashes(s: str) -> bool:
	"""Whether `s`, a wheel filename, has the correct number of `-`s expected of a valid wheel filename."""
	return len(os.path.basename(s).split('-')) in [5, 6]  # noqa: PTH119
