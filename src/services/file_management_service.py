import re
import os
import subprocess
from typing import Optional, List, Tuple

from fastapi import UploadFile


class FileManagementService:
    """Service class to handle file-related operations."""

    @staticmethod
    def validate_filename(filename: str) -> bool:
        """
        Validate filename using a regex pattern.

        Args:
            filename (str): Name of the file to validate

        Returns:
            bool: True if filename is valid, False otherwise
        """
        re_pattern = r"^[A-Za-z0-9_-]*$"
        return bool(re.match(re_pattern, filename))

    @staticmethod
    def ensure_temp_directory():
        """Ensure the temp directory exists."""
        os.makedirs("temp", exist_ok=True)

    @classmethod
    def upload_file(cls, file: UploadFile) -> int:
        """
        Upload a file to the temp directory.

        Args:
            file (UploadFile): File to be uploaded

        Returns:
            int: HTTP status code (201 for new file, 204 for existing file)
        """
        cls.ensure_temp_directory()

        if not cls.validate_filename(file.filename):
            return 400

        file_path = os.path.join("temp", file.filename)
        status_code = 201

        if os.path.exists(file_path):
            status_code = 204

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        return status_code

    @staticmethod
    def list_files(page: int = 1, limit: int = 10) -> List[str]:
        """
        List files with pagination.

        Args:
            page (int): Page number
            limit (int): Number of files per page

        Returns:
            List[str]: List of files for the specified page
        """
        files = os.listdir("temp")
        return files[(page - 1) * limit : page * limit]

    @staticmethod
    def run_shell_script(script_path: str, file_path: str, *args) -> str:
        """
        Run a shell script with given arguments.

        Args:
            script_path (str): Path to the shell script
            file_path (str): Path to the file to process
            *args: Additional arguments for the script

        Returns:
            str: Output of the shell script
        """
        cmd = ["bash", script_path, file_path, *args]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, _ = process.communicate()
        return result.decode().strip()

    @classmethod
    def get_size(cls, file_name: str, size_type: str = "max") -> Tuple[str, int]:
        """
        Get max or min size.

        Args:
            file_name (str): Name of the file
            size_type (str): Type of size to retrieve ('max' or 'min')

        Returns:
            str: Size
        """
        file_path = os.path.join("temp", file_name)

        if not os.path.exists(file_path):
            return "File not found", 404

        args = ["-min"] if size_type == "min" else []
        return cls.run_shell_script("scripts/max-min-size.sh", file_path, *args), 200

    @classmethod
    def list_users(
        cls,
        file_name: str,
        page: int = 1,
        limit: int = 10,
        name: Optional[str] = None,
        order: str = "asc",
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
    ) -> List[str]:
        """
        List users with various filtering and pagination options.

        Args:
            file_name (str): Name of the file to process
            page (int): Page number
            limit (int): Number of users per page
            name (Optional[str]): Filter users by name
            order (str): Sort order ('asc' or 'desc')
            min_val (Optional[int]): Minimum value for message count filter
            max_val (Optional[int]): Maximum value for message count filter

        Returns:
            List[str]: List of filtered and paginated users
        """
        file_path = os.path.join("temp", file_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found")

        # Determine which script to run based on parameters
        if min_val is not None and max_val is not None:
            users = cls.run_shell_script(
                "scripts/between-msgs.sh", file_path, str(min_val), str(max_val)
            ).split("\n")
        else:
            order_args = ["-desc"] if order == "desc" else []
            users = cls.run_shell_script(
                "scripts/order-by-username.sh", file_path, *order_args
            ).split("\n")

        # Apply name filter if provided
        if name:
            users = [user for user in users if name in user]

        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        return users[start:end]

    @staticmethod
    def file_exists(file_name: str) -> bool:
        """
        Check if a file exists in the temp directory.

        Args:
            file_name (str): Name of the file to check

        Returns:
            bool: True if the file exists, False otherwise
        """
        return os.path.exists(os.path.join("temp", file_name))
