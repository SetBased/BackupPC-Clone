import os
from pathlib import Path
from typing import List, Dict

from backuppc_clone.CloneIO import CloneIO


class AuxiliaryFileScanner:
    """
    Scans for auxiliary files.
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
    def scan(self, pc_path: Path) -> List[Dict]:
        """
        Scans recursively a directory for auxiliary of hosts.

        @param pc_path: The path to thePC directory, i.e. the directory where the host backups are stored.
        """
        self.__io.write_line(f' Scanning <fso>{pc_path}</fso>')

        hosts = []
        files = []
        for entry in os.scandir(pc_path):
            if entry.is_dir():
                hosts.append(entry.name)

        for host in hosts:
            host_dir = pc_path.joinpath(host)
            for entry in os.scandir(host_dir):
                if entry.is_file():
                    stats = os.stat(host_dir.joinpath(entry.name))
                    files.append({'host':  host,
                                  'name':  entry.name,
                                  'size':  stats.st_size,
                                  'mtime': stats.st_mtime})

        return files

# ------------------------------------------------------------------------------------------------------------------
