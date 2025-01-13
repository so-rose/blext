"""Runs when the package is executed.

Executes the `typer` app defined in `cli.py`.
"""

if __name__ == '__main__':
	from blext.cli import app

	app()
