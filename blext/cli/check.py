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

"""Implements `blext check`."""

import sys

import pydantic as pyd

import blext.exceptions as exc
from blext import blender, finders

from ._context import (
	APP,
	CONSOLE,
	DEFAULT_BLEXT_INFO,
	DEFAULT_CONFIG,
	ParameterBLExtInfo,
	ParameterConfig,
	ParameterProj,
)


@APP.command()
def check(
	proj: ParameterProj = None,
	*,
	blext_info: ParameterBLExtInfo = DEFAULT_BLEXT_INFO,
	global_config: ParameterConfig = DEFAULT_CONFIG,
) -> None:
	"""Check an extension project for problems.

	Parameters:
		proj: Location specifier for `blext` projects.
		blext_info: Information used to find and load `blext` project.
		global_config: Loaded global configuration.
	"""
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		blext_info = blext_info.parse_proj(proj)
		# blext_location = blext_info.blext_location(global_config)

	with exc.handle(exc.pretty, ValueError):
		blender_exe = finders.find_blender_exe(
			override_path_blender_exe=global_config.path_blender_exe
		)

	if blext_info.path is None:
		raise NotImplementedError

	check_target_name = blext_info.path.parts[-1]

	####################
	# - Packed ZIP
	####################
	if blext_info.path.name.endswith('.zip'):
		checks: dict[str, bool] = {
			'blender --command extension validate': False,
		}
		path_zip = blext_info.path

		####################
		# - Check: Validate w/Blender
		####################
		try:
			blender.validate_extension(blender_exe, path_zip=path_zip)
			checks['blender --command extension validate'] = True

		except ValueError:
			pass

	####################
	# - Script/Project
	####################
	else:
		checks: dict[str, bool] = {
			'Find Extension Specification': False,
			'Load Extension Specification': False,
		}
		####################
		# - Check: Load and Validate Specification
		####################
		try:
			_ = blext_info.blext_location(global_config)
			checks['Find Extension Specification'] = True
		except ValueError:
			pass

		try:
			blext_spec = blext_info.blext_spec(global_config)
			checks['Load Extension Specification'] = True

			check_target_name = blext_spec.id

		except (ValueError, pyd.ValidationError):
			pass

	####################
	# - Report
	####################
	if all(checks.values()):
		all_pass_str = r'\[[green]✓[/green]]'
	elif not any(checks.values()):
		all_pass_str = r'\[[red]X[/red]]'
	else:
		all_pass_str = r'\[[yellow]-[/yellow]]'

	checks_passed = len(
		[check_status for check_status in checks.values() if check_status]
	)
	checks_passed_str = f'{checks_passed}/{len(checks)}'

	CONSOLE.print()
	CONSOLE.print(
		all_pass_str + f' [bold]{check_target_name}[/bold] ({checks_passed_str})'
	)
	for check_text, check_status in checks.items():
		CONSOLE.print(
			'   ',
			r'\[[green]✓[/green]]' if check_status else r'\[[red]X[/red]]',
			' ',
			check_text,
			sep='',
		)

	####################
	# - Exit Code
	####################
	if not all(checks.values()):
		sys.exit(1)
