import os
import shutil
from typing import List, Tuple

class FileManager:
    """
    Static utility class for common file operations such as listing, renaming, moving, and copying video files.
    """

    @staticmethod
    def get_video_files(path: str, extensions: Tuple[str, ...] = ('.mkv', '.mp4', '.avi', '.mov')) -> List[str]:
        """
        Retrieves a list of video files from the specified directory.

        Parameters
        ----------
        path (str): Directory path to search for video files.
        extensions (Tuple[str, ...]): Supported video file extensions.

        Usage
        -----
        FileManager.get_video_files("/videos")

        Returns
        -------
        List[str]
            A list of full file paths to video files found in the directory.
        """
        return [
            os.path.join(path, file)
            for file in os.listdir(path)
            if file.lower().endswith(extensions)
        ]

    @staticmethod
    def rename_file(original_path: str, new_name: str) -> bool:
        """
        Renames a file to a new name in the same directory.

        Parameters
        ----------
        original_path (str): Full path to the original file.
        new_name (str): New file name (with extension).

        Usage
        -----
        FileManager.rename_file("path/video.mkv", "new_video.mkv")

        Returns
        -------
        bool
            True if the file was renamed successfully, False otherwise.
        """
        try:
            directory = os.path.dirname(original_path)
            new_path = os.path.join(directory, new_name)
            os.rename(original_path, new_path)
            return True

        except Exception as error:
            print(f"Rename error: {error}")
            return False

    @staticmethod
    def move_file(source: str, destination: str) -> bool:
        """
        Moves a file from source to destination path.

        Parameters
        ----------
        source (str): Source file path.
        destination (str): Destination file path.

        Usage
        -----
        FileManager.move_file("old_path/video.mkv", "new_path/video.mkv")

        Returns
        -------
        bool
            True if the file was moved successfully, False otherwise.
        """
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)
            return True
        
        except Exception as error:
            print(f"Move error: {error}")
            return False

    @staticmethod
    def copy_file(source: str, destination: str) -> bool:
        """
        Copies a file from source to destination path.

        Parameters
        ----------
        source (str): Source file path.
        destination (str): Destination file path.

        Usage
        -----
        FileManager.copy_file("video.mkv", "backup/video.mkv")

        Returns
        -------
        bool
            True if the file was copied successfully, False otherwise.
        """
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
            return True
        
        except Exception as error:
            print(f"Copy error: {error}")
            return False
