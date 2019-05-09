"""
BackupPC Clone
"""
import csv
import os
import shutil

from backuppc_clone.Config import Config
from backuppc_clone.ProgressBar import ProgressBar
from backuppc_clone.helper.BackupInfoScanner import BackupInfoScanner


class BackupScanner:
    """
    Helper class for scanning backup directories.
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

        self.__dir_count = 0
        """
        The file count.

        :type: int
        """

        self.__file_count = 0
        """
        The file count.

        :type: int
        """

        self.__entry_seq = 0
        """
        The entry sequence number.

        :type: int
        """

        self.progress = None
        """
        The progress counter.
        
        :type: backuppc_clone.ProgressBar.ProgressBar
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def dir_count(self):
        """
        Returns the number of found directories.

        :return: int
        """
        return self.__dir_count

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def file_count(self):
        """
        Returns the number of found files.

        :return: int
        """
        return self.__file_count

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_directory_helper(self, parent_dir, dir_name, csv_writer):
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
    def scan_directory(self, host, backup_no, csv_filename):
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

        with open(csv_filename, 'wt') as csv_file:
            csv_writer = csv.writer(csv_file)
            self.__io.writeln(' Scanning <fso>{}</fso>'.format(backup_dir))
            self.__io.writeln('')
            self.__scan_directory_helper(backup_dir, '', csv_writer)
            self.progress.finish()

    # ------------------------------------------------------------------------------------------------------------------
    def pre_scan_directory(self, host, backup_no):
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

        with open(csv_filename1, 'wt') as csv_file:
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
