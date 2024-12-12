import os
import pytest
import tempfile
import subprocess
from fastapi import UploadFile
from io import BytesIO
from unittest.mock import patch, mock_open, MagicMock

from src.services.file_management_service import (
    FileManagementService,
)


@pytest.fixture
def mock_upload_file():
    """Create a mock UploadFile object."""
    file_content = b"test content"
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_file"
    mock_file.file = BytesIO(file_content)
    return mock_file


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        with patch("os.makedirs") as mock_makedirs, patch(
            "os.path.join", side_effect=os.path.join
        ), patch("os.listdir", side_effect=os.listdir), patch(
            "os.path.exists", side_effect=os.path.exists
        ):
            mock_makedirs.return_value = None
            yield tmpdirname


def test_validate_filename():
    """Test filename validation."""
    assert FileManagementService.validate_filename("valid_file-123") == True
    assert FileManagementService.validate_filename("invalid file!") == False
    assert FileManagementService.validate_filename("") == True


def test_ensure_temp_directory(mocker):
    """Test creation of temp directory."""
    mock_makedirs = mocker.patch("os.makedirs")
    FileManagementService.ensure_temp_directory()
    mock_makedirs.assert_called_once_with("temp", exist_ok=True)


def test_upload_file(temp_directory, mock_upload_file):
    """Test file upload functionality."""
    # Mock file operations
    mock_open_func = mock_open()

    with patch("builtins.open", mock_open_func), patch(
        "os.path.exists", return_value=False
    ):

        # Test new file upload
        status_code = FileManagementService.upload_file(mock_upload_file)
        assert status_code == 201

        # Verify file was written
        mock_open_func.assert_called_once_with(os.path.join("temp", "test_file"), "wb")
        mock_open_func().write.assert_called_once_with(b"test content")

    # Test existing file upload
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open_func
    ):
        status_code = FileManagementService.upload_file(mock_upload_file)
        assert status_code == 204

    # Test invalid filename
    invalid_file = MagicMock(spec=UploadFile)
    invalid_file.filename = "invalid file!"
    status_code = FileManagementService.upload_file(invalid_file)
    assert status_code == 400


def test_list_files(temp_directory, mocker):
    """Test file listing with pagination."""
    # Mock listdir to return sample files
    mock_files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "file5.txt"]
    mocker.patch("os.listdir", return_value=mock_files)

    # Test first page
    files = FileManagementService.list_files(page=1, limit=2)
    assert files == ["file1.txt", "file2.txt"]

    # Test second page
    files = FileManagementService.list_files(page=2, limit=2)
    assert files == ["file3.txt", "file4.txt"]


@patch("subprocess.Popen")
def test_run_shell_script(mock_popen):
    """Test shell script execution."""
    # Mock subprocess
    mock_process = MagicMock()
    mock_process.communicate.return_value = (b"test output\n", b"")
    mock_popen.return_value = mock_process

    output = FileManagementService.run_shell_script(
        "test_script.sh", "test_file.txt", "arg1"
    )

    # Verify subprocess call
    mock_popen.assert_called_once_with(
        ["bash", "test_script.sh", "test_file.txt", "arg1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert output == "test output"


def test_get_size(temp_directory, mocker):
    """Test file size retrieval."""
    # Mock file existence and shell script execution
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch.object(FileManagementService, "run_shell_script", return_value="1024")

    # Test max size
    size, status = FileManagementService.get_size("test_file.txt")
    assert size == "1024"
    assert status == 200

    # Test min size
    size, status = FileManagementService.get_size("test_file.txt", size_type="min")

    # Test non-existent file
    mocker.patch("os.path.exists", return_value=False)
    size, status = FileManagementService.get_size("non_existent.txt")
    assert size == "File not found"
    assert status == 404


def test_list_users(temp_directory, mocker):
    """Test user listing with various filters."""
    # Mock file existence and shell script execution
    mocker.patch("os.path.exists", return_value=True)

    # Mock shell script to return sample users
    mock_users = ["user1:100", "user2:200", "user3:50", "user4:150"]

    # Test ordering and pagination
    with patch.object(
        FileManagementService, "run_shell_script", return_value="\n".join(mock_users)
    ):
        users = FileManagementService.list_users("test_file.txt")
        assert len(users) == 4

        # Test with name filter
        users = FileManagementService.list_users("test_file.txt", name="user2")
        assert users == ["user2:200"]

        # Test with message count filter
        with patch.object(
            FileManagementService,
            "run_shell_script",
            return_value="user2:200\nuser4:150",
        ):
            users = FileManagementService.list_users(
                "test_file.txt", min_val=100, max_val=200
            )
            assert len(users) == 2


def test_file_exists(temp_directory, mocker):
    """Test file existence check."""
    # Test existing file
    mocker.patch("os.path.exists", return_value=True)
    assert FileManagementService.file_exists("test_file.txt") == True

    # Test non-existing file
    mocker.patch("os.path.exists", return_value=False)
    assert FileManagementService.file_exists("non_existent.txt") == False
