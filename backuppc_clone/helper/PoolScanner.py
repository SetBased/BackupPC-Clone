import csv
import os
from pathlib import Path
from typing import List

from backuppc_clone.CloneIO import CloneIO
from backuppc_clone.ProgressBar import ProgressBar


class PoolScanner:
    """
    Helper class for scanning pool and backup directories.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io: CloneIO):
        """
        Object constructor.

        @param CloneIO io: The output style.
        """
        self.__io: CloneIO = io
        """
        The output style.
        """

        self.__file_count: int = 0
        """
        The file count.
        """

        self.__progress: ProgressBar | None = None
        """
        The progress bar.
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def count(self) -> int:
        """
        Returns the number of found files.
        """
        return self.__file_count

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __get_number_of_pool_dirs(dir_name: Path) -> int:
        """
        Returns the (estimated) number of directories in a pool.

        @param dir_name: The name of the directory.
        """
        if dir_name.joinpath('00').is_dir() and dir_name.joinpath('fe').is_dir():
            return 1 + 128 + 128 * 128

        return 1

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_directory_helper2(self, parent_path1: Path, dir_name: Path, csv_writer) -> None:
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        @param parent_path: The name of the parent directory.
        @param dir_name: The name of the directory.
        @param csv_writer: The CSV writer.
        """
        sub_dir_names = []
        for entry in os.scandir(parent_path1.joinpath(dir_name)):
            if entry.is_file():
                self.__file_count += 1
                csv_writer.writerow((entry.inode(), dir_name, entry.name))

            elif entry.is_dir():
                sub_dir_names.append(entry.name)

        for sub_dir_name in sub_dir_names:
            self.__scan_directory_helper2(parent_path1,  dir_name.joinpath(sub_dir_name), csv_writer)

        self.__progress.advance()

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_directory_helper1(self, parent_path: Path, dir_name: Path, csv_writer) -> None:
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        @param parent_path: The path to the parent directory.
        @param dir_name: The name of the directory.
        @param csv_writer: The CSV writer.
        """
        dir_target = parent_path.joinpath(dir_name)

        self.__io.write_line(f' Scanning <fso>{dir_target}</fso>')
        self.__io.write_line('')

        dir_count = self.__get_number_of_pool_dirs(dir_target)
        self.__progress = ProgressBar(self.__io, dir_count)

        self.__scan_directory_helper2(parent_path, dir_name, csv_writer)

        self.__progress.finish()
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def scan_directory(self, parent_path: Path, dir_names: List[str], csv_path: Path) -> None:
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        @param parent_dir: The path to the parent dir.
        @param dir_names: The list of directories to scan.
        @param csv_path: The path to the CSV file.
        """
        self.__file_count = 0

        with open(csv_path, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            if not dir_names:
                self.__scan_directory_helper1(parent_path, Path(''), csv_writer)
            else:
                for dir_name in dir_names:
                    self.__scan_directory_helper1(parent_path, Path(dir_name), csv_writer)

# ----------------------------------------------------------------------------------------------------------------------
