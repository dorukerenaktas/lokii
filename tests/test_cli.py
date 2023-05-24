from io import StringIO

from lokii import Lokii
from cli import execute_from_command_line, LOKII_ASCII


def test_execute_from_command_line_should_print_help(mocker):
    mock: StringIO = mocker.patch("sys.stdout", new=StringIO())
    execute_from_command_line("--help")
    assert LOKII_ASCII in mock.getvalue()
    Lokii.clean_env(force=True)
