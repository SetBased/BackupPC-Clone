"""
BackupPC Clone
"""
import csv
import os


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

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def count(self):
        """
        Returns the number of found files.

        :return: int
        """
        return self.__count

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_directory_helper(self, parent_dir, dir_name, csv_writer):
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
            self.__scan_directory_helper(parent_dir, os.path.join(dir_name, sub_dir_name), csv_writer)

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
                self.__io.writeln(' Scanning <fso>{}</fso>'.format(parent_dir))
                self.__scan_directory_helper(parent_dir, '', csv_writer)
            else:
                for dir_name in dir_names:
                    self.__io.writeln(' Scanning <fso>{}</fso>'.format(os.path.join(parent_dir, dir_name)))
                    self.__scan_directory_helper(parent_dir, dir_name, csv_writer)

# ----------------------------------------------------------------------------------------------------------------------
