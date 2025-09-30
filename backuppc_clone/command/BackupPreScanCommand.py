from cleo.helpers import argument

from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.helper.BackupScanner import BackupScanner


class BackupPreScanCommand(BaseCommand):
    """
    Pre-scans a host backup.
    """
    name = 'backup-pre-scan'
    description = 'Pre-scans a host backup.'
    arguments = [argument(name='clone.cfg', description='The configuration file of the clone.'),
                 argument(name='host', description='The name of the host.'),
                 argument(name='backup#', description='The backup number.')]

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self) -> None:
        """
        Executes the command.
        """
        host = self.argument('host')
        backup_no = int(self.argument('backup#'))

        self._io.title(f'Pre-Scanning Backup {host}/{backup_no}')

        helper = BackupScanner(self._io)
        helper.pre_scan_directory(host, backup_no)

        DataLayer.instance.commit()

# ----------------------------------------------------------------------------------------------------------------------
