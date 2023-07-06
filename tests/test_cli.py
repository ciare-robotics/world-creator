import os

from click.testing import CliRunner

from ciare_world_creator.cli import cli


def test_list():
    dir_ = "/var/tmp/ciare/"
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    _ = open(f"{dir_}openai_api_key", "a").close()
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0, result.output


def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0, result.output
    assert "No module named" not in result.output
