# Standard Library
from unittest.mock import patch, MagicMock, mock_open
from yaml import dump

# 3rd Party
import pytest
from munch import Munch, munchify

# Bittensor
from bittensor.commands.profile import *
from bittensor import config as bittensor_config

class MockDefaults:
    profile = {
        "name": "default",
        "path": "~/.bittensor/profiles/",
    }

@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            {
                "profile": {
                    "name": "EmptyProfile",
                },
            },
            "EmptyProfile",
        ),
        (
            {
                "profile": {
                    "name": "PopulatedProfile",
                },
                "wallet": {
                    "name": "test_wallet_name",
                    "hotkey": "test_wallet_hotkey",
                    "path": "test_wallet_path",
                },
                "subtensor": {
                    "network": "test_subtensor_network",
                },
                "netuid": "1",
            },
            "PopulatedProfile",
        ),
    ],
    ids=["EmptyProfile", "PopulatedProfile"],
)

@patch("bittensor.commands.profile.ProfileCreateCommand._write_profile")
@patch("bittensor.commands.profile.defaults", MockDefaults)
def test_create_profile(mock_write_profile, test_input, expected):
    # Arrange
    mock_cli = MagicMock()
    mock_cli.config = Munch(test_input.items())

    # Act
    ProfileCreateCommand.run(mock_cli)

    # Assert
    mock_write_profile.assert_called_once()
    assert mock_cli.config.profile["name"] == expected

@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            bittensor_config(),
            True,
        ),
        # Edge cases
        (
            None,
            False,
        ),
    ],
)
def test_check_config(test_input, expected):
    # Arrange - In this case, all inputs are provided via test parameters, so we omit the Arrange section.

    # Act
    result = ProfileCreateCommand.check_config(test_input)

    # Assert
    assert result == expected


def test_write_profile():
    config = munchify(
        {
            "profile": {
                "name": "test",
                "path": "~/.bittensor/profiles/",
            },
            "wallet": {
                "name": "test_wallet_name",
                "hotkey": "test_wallet_hotkey",
                "path": "test_wallet_path",
            },
            "subtensor": {
                "network": "test_subtensor_network",
            },
            "netuid": "1",
        },
    )
    path = config.profile.path
    name = config.profile.name

    # Setup the mock for os.makedirs and open
    with patch("os.makedirs") as mock_makedirs, patch(
        "os.path.expanduser", return_value=path
    ), patch("builtins.open", mock_open()) as mock_file:
        ProfileCreateCommand._write_profile(config)

        # Assert that makedirs was called correctly
        mock_makedirs.assert_called_once_with(config.profile["path"], exist_ok=True)

        # Assert that open was called correctly; construct the expected file path and contents
        expected_path = f"{path}/btcli-{name}.yaml"

        # Assert the open function was called correctly and the right contents were written
        mock_file.assert_called_once_with(expected_path, "w+")
        mock_file().write.assert_called_once_with(dump(config))

def test_get_profile_details_not_a_directory():
    with patch('os.path.isdir', return_value=False):
        result = ProfileListCommand.get_profile_details('not/a/real/directory')
        assert result == None

# Test when there are no matching files
def test_get_profile_details_no_matching_files():
    with patch('os.path.isdir', return_value=True):
        with patch('os.listdir', return_value=['file_not_matching_pattern.txt']):
            result = ProfileListCommand.get_profile_details('/some/directory')
            assert result == []

# Test when there are matching files
def test_get_profile_details_matching_files():
    with patch('os.path.isdir', return_value=True):
        with patch('os.listdir', return_value=['btcli-profile1.yaml', 'btcli-profile2.yaml', 'file_not_matching_pattern.yaml']):
            with patch('os.path.join', side_effect=lambda x, y: f"{x}/{y}"):
                with patch('os.path.getsize', side_effect=[123, 456]):
                    result = ProfileListCommand.get_profile_details('/profile/path')
                    expected_result = [
                        ('profile1', '/profile/path/btcli-profile1.yaml', "123 bytes"),
                        ('profile2', '/profile/path/btcli-profile2.yaml', "456 bytes")
                    ]
                    assert result == expected_result

def test_print_profile_details_empty():
    cli_mock = MagicMock()
    profile_path = '/profile/path'
    profile_details = []

    with patch('bittensor.__console__.print') as mock_print:
        ProfileListCommand.print_profile_details(cli_mock, profile_path, profile_details)
        mock_print.assert_called_once_with(":cross_mark: [red]No profiles found in '/profile/path'[/red]")

def test_print_profile_details_with_data():
    cli_mock = MagicMock()
    profile_path = '/profile/path'
    profile_details = [
        ('profile1', '/profile/path/btcli-profile1.yaml', "123 bytes"),
        ('profile2', '/profile/path/btcli-profile2.yaml', "456 bytes")
    ]
    active_profile = "profile1"

    with patch('bittensor.__console__.print') as mock_print:
        ProfileListCommand.print_profile_details(cli_mock, profile_path, profile_details, active_profile)
        # Here you would validate the actual table printed, which can be complex
        # depending on how the Table object is implemented and used.
        # For simplicity, we're just checking if the print method was called.
        assert mock_print.call_count == 1
        table = mock_print.call_args.args[0]
        assert table.row_count == 2
        # I don't know how to get the cell contents to check the Active column.
        # Maybe print to a string and pattern match it.

def test_print_profile_contents_with_data():
    cli_mock = MagicMock()
    profile_name = "test"
    profile_contents = munchify(
        {
            "profile": {
                "name": f"{profile_name}",
                "path": "~/.bittensor/profiles/",
            },
            "wallet": {
                "name": "test_wallet_name",
                "hotkey": "test_wallet_hotkey",
                "path": "test_wallet_path",
            },
            "subtensor": {
                "network": "test_subtensor_network",
            },
            "netuid": "1",
        },
    )

    with patch('bittensor.__console__.print') as mock_print:
        ProfilePrintCommand.print_profile_contents(cli_mock, profile_name, profile_contents)
        # Here you would validate the actual table printed, which can be complex
        # depending on how the Table object is implemented and used.
        # For simplicity, we're just checking if the print method was called.
        assert mock_print.call_count == 1
        table = mock_print.call_args.args[0]
        assert table.row_count == 7

def test_write_profile_to_disk_success(monkeypatch):
    profile_name = "test_profile_name"
    profile_path = '/profile/path'

    with patch('builtins.open') as mock_open, patch('bittensor.__console__.print') as mock_print:
        ProfileUseCommand.write_profile_to_disk(profile_name, profile_path)

        mock_open.assert_called_with(f"{profile_path}/.btcliprofile", 'w')
        #For some reason the return value here is a different instance than when called inside the method
        #mock_open.return_value.assert_called_with(profile_name)
        assert f"Profile set to {profile_name}." in mock_print.call_args.args[0]

def test_write_profile_to_disk_permission_error(monkeypatch):
    profile_name = "test_profile_name"
    profile_path = '/profile/path'

    with patch('builtins.open') as mock_open, patch('bittensor.__console__.print') as mock_print:
        mock_open.side_effect = PermissionError()
        ProfileUseCommand.write_profile_to_disk(profile_name, profile_path)
        assert f"Error: Profile not set." in mock_print.call_args.args[0]