"""
BackupPC Clone
"""
from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.helper.AuxiliaryFiles import AuxiliaryFiles
from backuppc_clone.helper.BackupDelete import BackupDelete
from backuppc_clone.helper.BackupInfoScanner import BackupInfoScanner
from backuppc_clone.helper.BackupClone import BackupClone
from backuppc_clone.helper.HostDelete import HostDelete
from backuppc_clone.helper.PoolSync import PoolSync


class AutoCommand(BaseCommand):
    """
    Clones the original in automatic mode

    auto
        {clone.cfg : The configuration file of the clone}
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_original_backups(self):
        """
        Scans the original hosts backups.
        """
        self._io.title('Inventorying Original Backups')

        helper = BackupInfoScanner(self._io)
        helper.scan()
        DataLayer.instance.commit()

    # ------------------------------------------------------------------------------------------------------------------
    def __remove_obsolete_hosts(self):
        """
        Removes obsolete hosts.
        """
        hosts = DataLayer.instance.host_get_obsolete()
        if hosts:
            self._io.title('Removing Obsolete Hosts')

            for host in hosts:
                helper = HostDelete(self._io)
                helper.delete_host(host['hst_name'])

                DataLayer.instance.commit()

    # ------------------------------------------------------------------------------------------------------------------
    def __remove_obsolete_backups(self):
        """
        Removes obsolete host backups.
        """
        backups = DataLayer.instance.backup_get_obsolete()
        if backups:
            self._io.title('Removing Obsolete Host Backups')

            for backup in backups:
                helper = BackupDelete(self._io)
                helper.delete_backup(backup['hst_name'], backup['bck_number'])

                DataLayer.instance.commit()

    # ------------------------------------------------------------------------------------------------------------------
    def __get_next_clone_target(self):
        """
        Returns the metadata of the host backup that needs to be cloned.

        :dict|None:
        """
        backup = DataLayer.instance.backup_get_next(Config.instance.last_pool_scan)
        if not backup:
            backup = DataLayer.instance.backup_get_next(-1)

        return backup

    # ------------------------------------------------------------------------------------------------------------------
    def __resync_pool(self, backup):
        """
        Resyncs the pool if required for cloning a backup.

        :param dict backup: The metadata of the backup.
        """
        if Config.instance.last_pool_scan < backup['bob_end_time']:
            self._io.title('Maintaining Clone Pool and Pool Metadata')

            helper = PoolSync(self._io)
            helper.synchronize()

            DataLayer.instance.commit()

    # ------------------------------------------------------------------------------------------------------------------
    def __clone_backup(self, backup):
        """
        Clones a backup.

        :param dict backup: The metadata of the backup.
        """
        self._io.title('Cloning Backup {}/{}'.format(backup['bob_host'], backup['bob_number']))

        helper = BackupClone(self._io)
        helper.clone_backup(backup['bob_host'], backup['bob_number'])

        DataLayer.instance.commit()

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self):
        """
        Executes the command.
        """
        while True:
            self.__scan_original_backups()
            self.__remove_obsolete_hosts()
            self.__remove_obsolete_backups()

            backup = self.__get_next_clone_target()
            if backup is None:
                break

            try:
                self.__resync_pool(backup)
                self.__clone_backup(backup)
            except FileNotFoundError as error:
                self._io.error(str(error))
                # Force resync of pool.
                Config.instance.last_pool_scan = -1
                DataLayer.instance.commit()

        helper = AuxiliaryFiles(self._io)
        helper.synchronize()

# ----------------------------------------------------------------------------------------------------------------------
