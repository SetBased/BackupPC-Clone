"""
BackupPC Clone
"""
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.helper.BackupClone import BackupClone


class BackupCloneCommand(BaseCommand):
    """
    Clones a single host backup

    backup-clone
        {clone.cfg : The configuration file of the clone}
        {host      : The name of the host}
        {backup#   : The backup number}
    """

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self):
        """
        Executes the command.
        """
        host = self.argument('host')
        backup_no = int(self.argument('backup#'))

        self._io.title('Cloning Backup {}/{}'.format(host, backup_no))

        helper = BackupClone(self._io)
        helper.clone_backup(host, backup_no)

        DataLayer.instance.commit()

# ----------------------------------------------------------------------------------------------------------------------
