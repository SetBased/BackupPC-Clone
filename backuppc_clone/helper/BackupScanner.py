"""
BackupPC Clone
"""
import csv
import os
import shutil
from typing import Optional

from backuppc_clone.Config import Config
from backuppc_clone.ProgressBar import ProgressBar
from backuppc_clone.helper.BackupInfoScanner import BackupInfoScanner
from backuppc_clone.style.BackupPcCloneStyle import BackupPcCloneStyle


class BackupScanner:
    """
    Helper class for scanning backup directories.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io: BackupPcCloneStyle):
        """
        Object constructor.

        :param BackupPcCloneStyle io: The output style.
        """

        self.__io: BackupPcCloneStyle = io
        """
        The output style.
        """

        self.__dir_count: int = 0
        """
        The file count.
        """

        self.__file_count: int = 0
        """
        The file count.
        """

        self.__entry_seq: int = 0
        """
        The entry sequence number.
        """

        self.progress: Optional[ProgressBar] = None
        """
        The progress counter.
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def dir_count(self) -> int:
        """
        Returns the number of found directories.

        :return: int
        """
        return self.__dir_count

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def file_count(self) -> int:
        """
        Returns the number of found files.

        :return: int
        """
        return self.__file_count

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_directory_helper(self, parent_dir: str, dir_name: str, csv_writer: csv.writer) -> None:
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        :param str parent_dir: The name of the parent directory.
        :param str dir_name: The name of the directory.
        :param csv.writer csv_writer: The CSV writer.
        """
        target_name = os.path.join(parent_dir, dir_name) if dir_name else parent_dir

        first_file = True
        sub_dir_names = []
        for entry in os.scandir(target_name):
            if entry.is_file():
                self.__file_count += 1
                if first_file:
                    first_file = False
                    self.__entry_seq += 1
                csv_writer.writerow((self.__entry_seq, entry.inode(), dir_name, entry.name))

                if entry.name not in ['attrib', 'backupInfo', 'backuppc-clone.csv']:
                    self.progress.advance()

            elif entry.is_dir():
                sub_dir_names.append(entry.name)

        for sub_dir_name in sorted(sub_dir_names):
            self.__entry_seq += 1
            self.__dir_count += 1
            csv_writer.writerow((self.__entry_seq, None, dir_name, sub_dir_name))
            self.__scan_directory_helper(parent_dir, os.path.join(dir_name, sub_dir_name), csv_writer)

    # ------------------------------------------------------------------------------------------------------------------
    def scan_directory(self, host: str, backup_no: int, csv_filename: str) -> None:
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        :param str host: The host name
        :param int backup_no: The backup number.
        :param str csv_filename: The filename of the CSV file.
        """
        self.__dir_count = 0
        self.__file_count = 0
        self.__entry_seq = 0

        backup_dir = Config.instance.backup_dir_original(host, backup_no)

        file_count = int(BackupInfoScanner.get_backup_info(backup_dir, 'nFiles'))
        self.progress = ProgressBar(self.__io.output, file_count)

        with open(csv_filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            self.__io.writeln(' Scanning <fso>{}</fso>'.format(backup_dir))
            self.__io.writeln('')
            self.__scan_directory_helper(backup_dir, '', csv_writer)
            self.progress.finish()

    # ------------------------------------------------------------------------------------------------------------------
    def pre_scan_directory(self, host: str, backup_no: int) -> None:
        """
        Scans recursively a list of directories and stores filenames and directories in CSV format.

        :param str host: The host name
        :param int backup_no: The backup number.
        """
        self.__dir_count = 0
        self.__file_count = 0
        self.__entry_seq = 0

        backup_dir = Config.instance.backup_dir_original(host, backup_no)

        csv_filename1 = os.path.join(Config.instance.tmp_dir_clone, '.backup-{}-{}.csv'.format(host, backup_no))
        csv_filename2 = os.path.join(backup_dir, 'backuppc-clone.csv')

        file_count = int(BackupInfoScanner.get_backup_info(backup_dir, 'nFiles'))
        self.progress = ProgressBar(self.__io.output, file_count)

        with open(csv_filename1, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            self.__io.writeln(' Scanning <fso>{}</fso>'.format(backup_dir))
            self.__io.writeln('')
            self.__scan_directory_helper(backup_dir, '', csv_writer)
            self.progress.finish()

        shutil.move(csv_filename1, csv_filename2)
        self.__io.writeln('')
        self.__io.writeln(' Wrote <fso>{}</fso>'.format(csv_filename2))
        self.__io.writeln('')

# ----------------------------------------------------------------------------------------------------------------------
