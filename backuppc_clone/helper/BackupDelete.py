import os

from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.CloneIO import CloneIO


class BackupDelete:
    """
    Deletes a backup of a host
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

        self.__host: str = ''
        """
        The host of the backup.
        """

        self.__backup_no: int = 0
        """
        The number of the backup.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __delete_files(self) -> None:
        """
        Removes the backup from the cone file system.
        """
        self.__io.write_line(' Removing files')

        backup_dir_clone = Config.instance.backup_clone_path(self.__host, self.__backup_no)
        if os.path.isdir(backup_dir_clone):
            os.system('rm -fr "%s"' % backup_dir_clone)

    # ------------------------------------------------------------------------------------------------------------------
    def __delete_metadata(self) -> None:
        """
        Removes the metadata from the database.
        """
        self.__io.write_line(' Removing metadata')

        hst_id = DataLayer.instance.get_host_id(self.__host)
        bck_id = DataLayer.instance.get_bck_id(hst_id, int(self.__backup_no))

        DataLayer.instance.backup_delete(bck_id)
        DataLayer.instance.commit()

    # ------------------------------------------------------------------------------------------------------------------
    def delete_backup(self, host: str, backup_no: int) -> None:
        """
        Deletes a backup of a host.

        @param str host: The host of the backup.
        @param int backup_no: The number of the backup.
        """
        self.__host = host
        self.__backup_no = backup_no

        self.__delete_metadata()
        self.__delete_files()

# ----------------------------------------------------------------------------------------------------------------------
