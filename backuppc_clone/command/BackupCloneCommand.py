from cleo.helpers import argument

from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.helper.BackupClone import BackupClone


class BackupCloneCommand(BaseCommand):
    """
    Clones a single host backup.
    """
    name = 'backup-clone'
    description = 'Clones a single host backup.'
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

        self._io.title(f'Cloning Backup {host}/{backup_no}')

        helper = BackupClone(self._io)
        helper.clone_backup(host, backup_no)

        DataLayer.instance.commit()

# ----------------------------------------------------------------------------------------------------------------------
