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

"""Implements `BLReleaseDiscovered`."""

import datetime as dtime
import functools
import typing as typ

import pydantic as pyd

from .bl_release_official import BLReleaseOfficial
from .bl_version import BLVersion


class BLReleaseDiscovered(pyd.BaseModel, frozen=True):
	"""Identifier for a supported version of Blender.

	Notes:
		Conforms to the `blext.extyp.bl_release.BLRelease` protocol.

	References:
		- Version Compatibility: <https://developer.blender.org/docs/release_notes/compatibility/>
	"""

	official_version: tuple[int, int, int]

	build_datetime: dtime.datetime
	build_commit_datetime: dtime.datetime
	build_hash: str
	build_branch: str
	build_platform: str
	build_type: str

	build_c_flags: tuple[str, ...]
	build_cpp_flags: tuple[str, ...]
	build_link_flags: tuple[str, ...]
	build_system: str

	####################
	# - Creation
	####################
	@classmethod
	def from_blender_version_output(cls, blender_version_output: str) -> typ.Self:  # noqa: C901
		"""Parse the output of `blender --version` to create this object."""
		lines = [
			line.strip()
			for line in blender_version_output.strip().split('\n')
			if line.strip()
		]

		####################
		# - Stage 0: Parse Fields
		####################
		if lines[0].startswith('Blender'):
			official_version_str = lines[0].split(' ')[1]
			official_version = tuple(int(el) for el in official_version_str.split('.'))
			if len(official_version) != 3:  # noqa: PLR2004
				msg = [
					"First line of `blender --version` string doesn't contain an official `M.m.p` version of Blender.",
					f'> First line of `blender --version`: {lines[0]}',
				]
				raise ValueError(msg)
		else:
			msgs = [
				"First line of `blender --version` string doesn't start with `Blender`.",
				f'> First line of `blender --version`: {lines[0]}',
			]
			raise ValueError(*msgs)

		parsed: dict[str, typ.Any] = {}
		for line in filter(lambda line: ':' in line, lines[1:]):
			line_split = line.split(':')
			match line_split[0]:
				case 'build date' | 'build commit date':
					parsed[line_split[0].replace(' ', '_')] = dtime.date.fromisoformat(
						line_split[1].strip()
					)

				case 'build time' | 'build commit time':
					parsed[line_split[0].replace(' ', '_')] = dtime.time.fromisoformat(
						line_split[1].strip()
					)

				case (
					'build hash'
					| 'build branch'
					| 'build platform'
					| 'build type'
					| 'build system'
				):
					parsed[line_split[0].replace(' ', '_')] = line_split[1].strip()

				case 'build c flags' | 'build c++ flags' | 'build link flags':
					parsed[line_split[0].replace(' ', '_').replace('++', 'pp')] = tuple(
						flag.strip()
						for flag in line_split[1].strip().split(' ')
						if flag.strip()
					)

				case _:
					msgs = [
						'Tried to parse unknown line from `blender --version`.',
						f'> Invalid line of `blender --version`: {line}',
					]
					raise ValueError(*msgs)

		missing_keys: list[str] = []
		for key in [
			'build_date',
			'build_time',
			'build_commit_date',
			'build_commit_time',
			'build_hash',
			'build_branch',
			'build_platform',
			'build_type',
			'build_c_flags',
			'build_cpp_flags',
			'build_link_flags',
			'build_system',
		]:
			if key not in parsed:
				missing_keys.append(key)

		if not missing_keys:
			return cls(
				official_version=official_version,
				build_datetime=dtime.datetime.combine(
					date=parsed['build_date'],  # pyright: ignore[reportAny]
					time=parsed['build_time'],  # pyright: ignore[reportAny]
				),
				build_commit_datetime=dtime.datetime.combine(
					date=parsed['build_commit_date'],  # pyright: ignore[reportAny]
					time=parsed['build_commit_time'],  # pyright: ignore[reportAny]
				),
				build_hash=parsed['build_hash'],  # pyright: ignore[reportAny]
				build_branch=parsed['build_branch'],  # pyright: ignore[reportAny]
				build_platform=parsed['build_platform'],  # pyright: ignore[reportAny]
				build_type=parsed['build_type'],  # pyright: ignore[reportAny]
				build_c_flags=parsed['build_c_flags'],  # pyright: ignore[reportAny]
				build_cpp_flags=parsed['build_cpp_flags'],  # pyright: ignore[reportAny]
				build_link_flags=parsed['build_link_flags'],  # pyright: ignore[reportAny]
				build_system=parsed['build_system'],  # pyright: ignore[reportAny]
			)

		msgs = [
			f'`blender --version` did not contain {len(missing_keys)} expected keys:',
			*[f' - {missing_key}' for missing_key in missing_keys],
		]
		raise ValueError(*msgs)

	####################
	# - Transformation
	####################
	@functools.cached_property
	def bl_version(self) -> BLVersion:
		"""The Blender version corresponding to this release."""
		official_version_str = '.'.join(str(el) for el in self.official_version)
		if official_version_str in set(BLReleaseOfficial):
			bl_release_official: BLReleaseOfficial = getattr(
				BLReleaseOfficial, 'BL' + official_version_str.replace('.', '_')
			)
			return bl_release_official.bl_version

		raise NotImplementedError
