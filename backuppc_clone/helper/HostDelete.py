"""
BackupPC Clone
"""
import os
import shutil

from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.style.BackupPcCloneStyle import BackupPcCloneStyle


class HostDelete:
    """
    Deletes a host entirely frm the clone.
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

        self.__host: str = ''
        """
        The host of the backup.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __delete_files(self) -> None:
        """
        Removes the host from the clone file system.
        """
        self.__io.writeln(' Removing files')

        host_dir_clone = Config.instance.host_dir_clone(self.__host)
        if os.path.isdir(host_dir_clone):
            os.system('rm -fr "%s"' % host_dir_clone)

    # ------------------------------------------------------------------------------------------------------------------
    def __delete_metadata(self) -> None:
        """
        Removes the metadata from the database.
        """
        self.__io.writeln(' Removing metadata')

        DataLayer.instance.host_delete(self.__host)
        DataLayer.instance.commit()

    # ------------------------------------------------------------------------------------------------------------------
    def delete_host(self, host: str) -> None:
        """
        Deletes a backup of a host.

        :param str host: The name of the host.
        """
        self.__host = host

        self.__delete_metadata()
        self.__delete_files()

# ----------------------------------------------------------------------------------------------------------------------
