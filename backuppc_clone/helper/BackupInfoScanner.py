"""
BackupPC Clone
"""
import os
import re

from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer


class BackupInfoScanner:
    """
    Class for retrieving information about backups.
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

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_backup_info(backup_dir, param_name):
        """
        Extracts info about a backup from file backupInfo.

        :param str backup_dir: The path to the host backup.
        :param str param_name: The name of the info parameter.

        :rtype: str|None
        """
        ret = None

        path = os.path.join(backup_dir, 'backupInfo')
        if os.path.isfile(path):
            with open(path) as file:
                content = file.read()
                result = re.search(r"'{}' => '(.*?)'".format(param_name), content)
                if result:
                    ret = result.group(1)

        if not ret:
            ret = None

        return ret

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_for_backups(self):
        """
        Scans for host backups and returns the metadata of the host backups.

        :rtype: list[dict]
        """
        pc_dir_original = Config.instance.pc_dir_original

        self.__io.writeln(' Scanning <fso>{}</fso>'.format(pc_dir_original))

        backups = []
        for host in os.scandir(pc_dir_original):
            if host.is_dir():
                host_dir = os.path.join(Config.instance.pc_dir_original, host.name)
                for backup in os.scandir(host_dir):
                    if backup.is_dir() and re.match(r'^\d+$', backup.name):
                        backup_dir = os.path.join(host_dir, backup.name)
                        backups.append({'bob_host':     host.name,
                                        'bob_number':   int(backup.name),
                                        'bob_end_time': self.get_backup_info(backup_dir, 'endTime'),
                                        'bob_version':  self.get_backup_info(backup_dir, 'version'),
                                        'bob_level':    self.get_backup_info(backup_dir, 'level'),
                                        'bob_type':     self.get_backup_info(backup_dir, 'type')})

        return backups

    # ------------------------------------------------------------------------------------------------------------------
    def __import_backups(self, backups):
        """
        Imports the original host backups info into the SQLite database.

        :param list[dict] backups: The metadata of the original backups.
        """
        DataLayer.instance.original_backup_truncate()

        for backup in backups:
            DataLayer.instance.original_backup_insert(backup['bob_host'],
                                                      backup['bob_number'],
                                                      backup['bob_end_time'],
                                                      backup['bob_version'],
                                                      backup['bob_level'],
                                                      backup['bob_type'])

        stats = DataLayer.instance.original_backup_get_stats()

        self.__io.writeln('')
        self.__io.writeln(' Found {} hosts and {} backups'.format(stats['#hosts'], stats['#backups']))
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def scan(self):
        """
        Scans information about backups.
        """
        backups = self.__scan_for_backups()
        self.__import_backups(backups)

# ----------------------------------------------------------------------------------------------------------------------
