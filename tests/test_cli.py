import contextlib

from typer.testing import CliRunner

from blext.cli import app
from tests import context

runner = CliRunner()


def test_build_simple():
	with contextlib.chdir(context.PATH_EXAMPLES['simple']):
		result = runner.invoke(app, ['build'])
		print(result)
		assert result.exit_code == 0
