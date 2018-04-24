"""
BackupPC Clone
"""
import os


class AuxiliaryFileScanner:
    """
    Scans for auxiliary files.
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
    def scan(self, pc_dir):
        """
        Scans recursively a directory for auxiliary of hosts.

        :param str pc_dir: The PC dir, i.e. the directory where the host backups are stored.
        """

        self.__io.writeln(' Scanning <fso>{}</fso>'.format(pc_dir))

        hosts = []
        files = []
        for entry in os.scandir(pc_dir):
            if entry.is_dir():
                hosts.append(entry.name)

        for host in hosts:
            host_dir = os.path.join(pc_dir, host)
            for entry in os.scandir(host_dir):
                if entry.is_file():
                    stats = os.stat(os.path.join(host_dir, entry.name))
                    files.append({'host':  host,
                                  'name':  entry.name,
                                  'size':  stats.st_size,
                                  'mtime': stats.st_mtime})

        return files

# ------------------------------------------------------------------------------------------------------------------
