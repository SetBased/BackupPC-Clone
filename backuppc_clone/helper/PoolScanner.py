"""
BackupPC Clone
"""
import csv
import os

from backuppc_clone.ProgressBar import ProgressBar


class PoolScanner:
    """
    Helper class for scanning pool and backup directories.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io):
        """
        Object constructor.

        :param backuppc_clone.style.BackupPcCloneStyle.BackupPcCloneStyle io: The output style.
        """

        self.__io = io
        """
        The output style.

        :type: backuppc_clone.style.BackupPcCloneStyle.BackupPcCloneStyle
        """

        self.__count = 0
        """
        The file count.

        :type: int
        """

        self.__progress = None
        """
        The progress bar.

        :type: backuppc_clone.ProgressBar.ProgressBar|None
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def count(self):
        """
        Returns the number of found files.

        :return: int
        """
        return self.__count

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __get_number_of_pool_dirs(dir_name):
        """
        Returns the (estimate) number of directories in a pool.

        :param str dir_name: The name of the directory.

        :rtype: int
        """
        if os.path.isdir(os.path.join(dir_name, '0')) and \
                os.path.isdir(os.path.join(dir_name, 'f')):
            return 1 + 16 + 16 * 16 + 16 * 16 * 16

        return 1

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_directory_helper2(self, parent_dir, dir_name, csv_writer):
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        :param str parent_dir: The name of the parent directory.
        :param str dir_name: The name of the directory.
        :param csv.writer csv_writer: The CSV writer.
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
    def __scan_directory_helper1(self, parent_dir, dir_name, csv_writer):
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        :param str parent_dir: The name of the parent directory.
        :param str dir_name: The name of the directory.
        :param csv.writer csv_writer: The CSV writer.
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
    def scan_directory(self, parent_dir, dir_names, csv_filename):
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        :param str parent_dir: The name of the parent dir.
        :param list[str] dir_names: The list of directories to scan.
        :param str csv_filename: The filename of the CSV file.
        """
        self.__count = 0

        with open(csv_filename, 'wt') as csv_file:
            csv_writer = csv.writer(csv_file)
            if not dir_names:
                self.__scan_directory_helper1(parent_dir, '', csv_writer)
            else:
                for dir_name in dir_names:
                    self.__scan_directory_helper1(parent_dir, dir_name, csv_writer)

# ----------------------------------------------------------------------------------------------------------------------
