from unittest.mock import patch, MagicMock

from package_dev_utils.tests.args import no_cli_args

from colortheme import cli


@patch("colortheme.main.main.main")
@no_cli_args
def test_entry_point(patched_main: MagicMock) -> None:
    cli.entry_point()
    patched_main.assert_called_once()
