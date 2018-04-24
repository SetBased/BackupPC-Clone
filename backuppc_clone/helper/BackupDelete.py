"""
BackupPC Clone
"""
import os
import shutil

from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer


class BackupDelete:
    """
    Deletes a backup of a host
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

        self.__backup_no = 0
        """
        The number of the backup.

        :type: int
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __delete_files(self):
        """
        Removes the backup from the cone file system.
        """
        self.__io.writeln(' Removing files')

        backup_dir_clone = Config.instance.backup_dir_clone(self.__host, self.__backup_no)
        if os.path.isdir(backup_dir_clone):
            shutil.rmtree(backup_dir_clone)

    # ------------------------------------------------------------------------------------------------------------------
    def __delete_metadata(self):
        """
        Removes the metadata from the database.
        """
        self.__io.writeln(' Removing metadata')

        hst_id = DataLayer.instance.get_host_id(self.__host)
        bck_id = DataLayer.instance.get_bck_id(hst_id, int(self.__backup_no))

        DataLayer.instance.backup_delete(bck_id)

    # ------------------------------------------------------------------------------------------------------------------
    def delete_backup(self, host, backup_no):
        """
        Deletes a backup of a host.

        :param str host: The host of the backup.
        :param int|str backup_no: The number of the backup.
        """
        self.__host = host
        self.__backup_no = backup_no

        self.__delete_metadata()
        self.__delete_files()

# ----------------------------------------------------------------------------------------------------------------------
