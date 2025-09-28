import re
from pathlib import Path
from typing import Dict, List

from backuppc_clone.CloneIO import CloneIO
from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer


class BackupInfoScanner:
    """
    Class for retrieving information about backups.
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

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_backup_info(backup_dir: Path, param_name: str) -> str | None:
        """
        Extracts info about a backup from file backupInfo.

        @param backup_dir: The path to the host backup.
        @param param_name: The name of the info parameter.
        """
        content = backup_dir.joinpath('backupInfo').read_text()
        result = re.search(r"'{}' => '(.*?)'".format(param_name), content)
        if result:
            return result.group(1)

        return None

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_for_backups(self) -> List[Dict]:
        """
        Scans for host backups and returns the metadata of the host backups.

        :rtype: list[dict]
        """
        pc_dir_original = Config.instance.pc_original_path

        self.__io.write_line(f' Scanning <fso>{pc_dir_original}</fso>')

        backups = []
        for pc_child in pc_dir_original.iterdir():
            if pc_child.is_dir():
                host_dir = pc_dir_original.joinpath(pc_child)
                for host_child in host_dir.iterdir():
                    if host_child.is_dir():
                        backup_dir = host_dir.joinpath(host_child)
                        if self.__is_a_backuppc_v4(host_child):
                            backups.append({'bob_host':     pc_child.name,
                                            'bob_number':   int(host_child.name),
                                            'bob_end_time': self.get_backup_info(backup_dir, 'endTime'),
                                            'bob_level':    self.get_backup_info(backup_dir, 'level'),
                                            'bob_type':     self.get_backup_info(backup_dir, 'type')})

        return backups

    # ------------------------------------------------------------------------------------------------------------------
    def __is_a_backuppc_v4(self, path: Path) -> bool:
        """
        Returns whether a path is a BackupPC V4 backup.

        :param path: The path.
        """
        if not re.match(r'^\d+$', path.name):
            return False

        for child in path.iterdir():
            if re.match(r'^attrib_[0-9a-f]+$', child.name):
                return True

        return False

    # ------------------------------------------------------------------------------------------------------------------
    def __import_backups(self, backups: List[Dict]) -> None:
        """
        Imports the original host backups info into the SQLite database.

        @param list[dict] backups: The metadata of the original backups.
        """
        DataLayer.instance.original_backup_truncate()

        for backup in backups:
            DataLayer.instance.original_backup_insert(backup['bob_host'],
                                                      backup['bob_number'],
                                                      backup['bob_end_time'],
                                                      backup['bob_level'],
                                                      backup['bob_type'])

        stats = DataLayer.instance.original_backup_get_stats()

        self.__io.write_line('')
        self.__io.write_line(f" Found {stats['#hosts']} hosts and {stats['#backups']} backups")
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def scan(self) -> None:
        """
        Scans information about backups.
        """
        backups = self.__scan_for_backups()
        self.__import_backups(backups)

# ----------------------------------------------------------------------------------------------------------------------
