"""
BackupPC Clone
"""
import os

from cleo import Output

from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.helper.AuxiliaryFiles import AuxiliaryFiles
from backuppc_clone.helper.BackupClone import BackupClone
from backuppc_clone.helper.BackupDelete import BackupDelete
from backuppc_clone.helper.BackupInfoScanner import BackupInfoScanner
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
    def __sync_auxiliary_files(self):
        """
        Synchronises auxiliary files (i.e. files directly under a host directory but not part of a backup).
        """
        self._io.title('Synchronizing Auxiliary Files')

        helper = AuxiliaryFiles(self._io)
        helper.synchronize()

    # ------------------------------------------------------------------------------------------------------------------
    def __show_overview_stats(self):
        """
        Shows the number of backups, cloned backups, backups to clone, and number of obsolete cloned backups.
        """
        stats = DataLayer.instance.overview_get_stats()

        self._io.writeln(' # backups                : {}'.format(stats['n_backups']))
        self._io.writeln(' # cloned backups         : {}'.format(stats['n_cloned_backups']))
        self._io.writeln(' # backups still to clone : {}'.format(stats['n_not_cloned_backups']))
        self._io.writeln(' # obsolete cloned backups: {}'.format(stats['n_obsolete_cloned_backups']))
        self._io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def __remove_obsolete_hosts(self):
        """
        Removes obsolete hosts.
        """
        hosts = DataLayer.instance.host_get_obsolete()
        if hosts:
            self._io.title('Removing Obsolete Hosts')

            for host in hosts:
                self._io.section('Removing host {}'.format(host['hst_name']))

                helper = HostDelete(self._io)
                helper.delete_host(host['hst_name'])

                DataLayer.instance.commit()

                self._io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def __remove_obsolete_backups(self):
        """
        Removes obsolete host backups.
        """
        backups = DataLayer.instance.backup_get_obsolete()
        if backups:
            self._io.title('Removing Obsolete Host Backups')

            for backup in backups:
                self._io.section('Removing backup {}/{}'.format(backup['hst_name'], backup['bck_number']))

                helper = BackupDelete(self._io)
                helper.delete_backup(backup['hst_name'], backup['bck_number'])

                DataLayer.instance.commit()

                self._io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def __remove_partially_cloned_backups(self):
        """
        Removes backups that are still marked "in progress" (and hence cloned partially).
        """
        backups = DataLayer.instance.backup_partially_cloned()
        if backups:
            self._io.title('Removing Partially Cloned Host Backups')

            for backup in backups:
                self._io.section('Removing backup {}/{}'.format(backup['hst_name'], backup['bck_number']))

                helper = BackupDelete(self._io)
                helper.delete_backup(backup['hst_name'], backup['bck_number'])

                DataLayer.instance.commit()

                self._io.writeln('')

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
    def __handle_file_not_found(self, backup, error):
        """
        Handles a FileNotFoundError exception.

        :param dict backup: The metadata of the backup.
        :param FileNotFoundError error: The exception.
        """
        if self._io.get_verbosity() >= Output.VERBOSITY_VERBOSE:
            self._io.warning(str(error))

        self._io.block('Resynchronization of the pool is required')

        # The host backup might been partially cloned.
        helper = BackupDelete(self._io)
        helper.delete_backup(backup['bob_host'], backup['bob_number'])

        # Force resynchronization of pool.
        Config.instance.last_pool_scan = -1

        # Commit the transaction.
        DataLayer.instance.commit()

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self):
        """
        Executes the command.
        """
        DataLayer.instance.disconnect()

        while True:
            pid = os.fork()

            if pid == 0:
                DataLayer.instance.connect()

                self.__remove_partially_cloned_backups()
                self.__scan_original_backups()
                self.__show_overview_stats()
                self.__remove_obsolete_hosts()
                self.__remove_obsolete_backups()

                backup = self.__get_next_clone_target()
                if backup is None:
                    exit(1)

                try:
                    self.__resync_pool(backup)
                    self.__clone_backup(backup)
                except FileNotFoundError as error:
                    self.__handle_file_not_found(backup, error)

                exit(0)

            pid, status = os.wait()
            if status != 0:
                break

        self.__sync_auxiliary_files()

# ----------------------------------------------------------------------------------------------------------------------
