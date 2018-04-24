"""
BackupPC Clone
"""
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.helper.BackupDelete import BackupDelete


class BackupDeleteCommand(BaseCommand):
    """
    Deletes a host backup

    backup-delete
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

        self._io.title('Deleting Backup {}/{}'.format(host, backup_no))

        helper = BackupDelete(self._io)
        helper.delete_backup(host, backup_no)

        DataLayer.instance.commit()

# ----------------------------------------------------------------------------------------------------------------------
