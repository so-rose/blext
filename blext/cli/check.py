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

"""Implements the `check` command."""

import sys
import typing as typ
from pathlib import Path

import pydantic as pyd

import blext.exceptions as exc
from blext import blender, extyp, finders, loaders

from ._context import APP, CONSOLE


@APP.command()
def check(
	path: Path | None = None,
	*,
	platform: extyp.BLPlatform | typ.Literal['detect'] | None = None,
) -> None:
	"""[Check] an extension without building it, or a built `.zip` for validity.

	Parameters:
		path: Path to an extension project, or an already-built `.zip`.
		platform: Blender platform(s) to constrain validation.
			Use "detect" to constrain to detect the current platform.
	"""
	with exc.handle(exc.pretty, ValueError):
		blender_exe = finders.find_blender_exe()

	checks: dict[str, bool] = {}

	####################
	# - Check ZIP
	####################
	if path is not None and path.name.endswith('.zip'):
		# CONSOLE.print('Checking [bold]built extension[/bold]:', str(path))

		# TODO: Specification validation from .zip
		# checks['blender_manifest.toml ([italic]not implemented[/italic])'] = False
		# CONSOLE.print(
		# f'    ...[italic]skipping since check is not yet implemented.[/italic]'
		# )

		####################
		# - Check: Validate w/Blender
		####################
		checks['blender --command extension validate'] = True
		try:
			blender.validate_extension(blender_exe, path_zip=path)
		except ValueError:
			checks['$ blender --command extension validate'] = False

		# TODO: Parse it to a BLExtSpec and check up on:
		## - Wheels: All from PyPi? Hashes OK? Dependency resolution OK?

	####################
	# - Check Project
	####################
	else:
		####################
		# - Check: Load and Validate Specification
		####################
		checks['Load Extension Specification'] = True
		checks['Validate Extension Specification'] = True
		try:
			_ = loaders.load_bl_platform_into_spec(
				loaders.load_blext_spec(
					proj_uri=path,
					release_profile_id='release',
				),
				bl_platform_ref=platform,
			)
		except (ValueError, pyd.ValidationError) as ex:
			if isinstance(ex, ValueError):
				checks['Load Extension Specification'] = False
			if isinstance(ex, pyd.ValidationError):
				checks['Validate Extension Specification'] = False

		# TODO: Really, most of the cheap checks should be part of BLExtSpec. However, what could be interesting is project-defined checks such as:
		## - tools [ruff, basedpyright, pytest]: Does the extension project pass checks made by project-defined tooling?
		## - Custom: User-defined checks in pyproject.toml / script metadata?

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
	CONSOLE.print(all_pass_str + f' [bold]{path}[/bold] ({checks_passed_str})')
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
	else:
		sys.exit(0)
