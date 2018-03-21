"""
BackupPC Clone
"""
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.helper.BackupScanner import BackupScanner


class BackupPreScanCommand(BaseCommand):
    """
    Pre-scans a host backup

    backup-pre-scan
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

        self._io.title('Pre-Scanning Backup {}/{}'.format(host, backup_no))

        helper = BackupScanner(self._io)
        helper.pre_scan_directory(host, backup_no)

        DataLayer.instance.commit()

# ----------------------------------------------------------------------------------------------------------------------
