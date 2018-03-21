"""
BackupPC Clone
"""
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.helper.HostDelete import HostDelete


class HostDeleteCommand(BaseCommand):
    """
    Deletes all backups and metadata of a host

    host-delete
        {clone.cfg : The configuration file of the clone}
        {host      : The name of the host}
    """

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self):
        """
        Executes the command.
        """
        host = self.argument('host')

        self._io.title('Deleting Host {}'.format(host))

        helper = HostDelete(self._io)
        helper.delete_host(host)

        DataLayer.instance.commit()

# ----------------------------------------------------------------------------------------------------------------------
