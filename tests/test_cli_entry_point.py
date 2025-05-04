from unittest.mock import MagicMock, patch

from package_dev_utils.tests.args import no_cli_args

from colortheme import cli


@patch("colortheme.main.eventchecker.EventChecker.start")
@no_cli_args
def test_entry_point(patched_start: MagicMock) -> None:
    cli.entry_point()
    patched_start.assert_called_once()
