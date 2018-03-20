"""
BackupPC Clone
"""
import os
import shutil

from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer


class HostDelete:
    """
    Deletes a host entirely frm the clone.
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

        self.__host = ''
        """
        The host of the backup.

        :type: str
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __delete_files(self, ):
        """
        Removes the host from the clone file system.
        """
        self.__io.writeln(' Removing files')

        host_dir_clone = Config.instance.host_dir_clone(self.__host)
        if os.path.isdir(host_dir_clone):
            shutil.rmtree(host_dir_clone)

    # ------------------------------------------------------------------------------------------------------------------
    def __delete_metadata(self):
        """
        Removes the metadata from the database.
        """
        self.__io.writeln(' Removing metadata')

        DataLayer.instance.host_delete(self.__host)

    # ------------------------------------------------------------------------------------------------------------------
    def delete_host(self, host):
        """
        Deletes a backup of a host.

        :param str host: The name of the host.
        """
        self.__host = host

        self.__delete_metadata()
        self.__delete_files()

# ----------------------------------------------------------------------------------------------------------------------
