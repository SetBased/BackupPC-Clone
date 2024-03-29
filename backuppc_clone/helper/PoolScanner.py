import csv
import os
from typing import List, Optional

from backuppc_clone.ProgressBar import ProgressBar
from backuppc_clone.style.BackupPcCloneStyle import BackupPcCloneStyle


class PoolScanner:
    """
    Helper class for scanning pool and backup directories.
    """
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io: BackupPcCloneStyle):
        """
        Object constructor.

        @param BackupPcCloneStyle io: The output style.
        """
        self.__io: BackupPcCloneStyle = io
        """
        The output style.
        """

        self.__count: int = 0
        """
        The file count.
        """

        self.__progress: Optional[ProgressBar] = None
        """
        The progress bar.
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def count(self) -> int:
        """
        Returns the number of found files.
        """
        return self.__count

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __get_number_of_pool_dirs(dir_name: str) -> int:
        """
        Returns the (estimate) number of directories in a pool.

        @param str dir_name: The name of the directory.

        :rtype: int
        """
        if os.path.isdir(os.path.join(dir_name, '0')) and \
                os.path.isdir(os.path.join(dir_name, 'f')):
            return 1 + 16 + 16 * 16 + 16 * 16 * 16

        return 1

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_directory_helper2(self, parent_dir: str, dir_name: str, csv_writer: csv.writer) -> None:
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        @param str parent_dir: The name of the parent directory.
        @param str dir_name: The name of the directory.
        @param csv.writer csv_writer: The CSV writer.
        """
        sub_dir_names = []
        for entry in os.scandir(os.path.join(parent_dir, dir_name)):
            if entry.is_file():
                self.__count += 1
                csv_writer.writerow((entry.inode(), dir_name, entry.name))

            elif entry.is_dir():
                sub_dir_names.append(entry.name)

        for sub_dir_name in sub_dir_names:
            self.__scan_directory_helper2(parent_dir, os.path.join(dir_name, sub_dir_name), csv_writer)

        self.__progress.advance()

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_directory_helper1(self, parent_dir: str, dir_name: str, csv_writer: csv.writer) -> None:
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        @param str parent_dir: The name of the parent directory.
        @param str dir_name: The name of the directory.
        @param csv.writer csv_writer: The CSV writer.
        """
        dir_target = os.path.join(parent_dir, dir_name)

        self.__io.writeln(' Scanning <fso>{}</fso>'.format(dir_target))
        self.__io.writeln('')

        dir_count = self.__get_number_of_pool_dirs(dir_target)
        self.__progress = ProgressBar(self.__io, dir_count)

        self.__scan_directory_helper2(parent_dir, dir_name, csv_writer)

        self.__progress.finish()
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def scan_directory(self, parent_dir: str, dir_names: List[str], csv_filename: str) -> None:
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        @param str parent_dir: The name of the parent dir.
        @param list[str] dir_names: The list of directories to scan.
        @param str csv_filename: The filename of the CSV file.
        """
        self.__count = 0

        with open(csv_filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            if not dir_names:
                self.__scan_directory_helper1(parent_dir, '', csv_writer)
            else:
                for dir_name in dir_names:
                    self.__scan_directory_helper1(parent_dir, dir_name, csv_writer)

# ----------------------------------------------------------------------------------------------------------------------
