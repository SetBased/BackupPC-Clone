"""
BackupPC Clone
"""
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.helper.PoolSync import PoolSync


class PoolCommand(BaseCommand):
    """
    Inventories the original pool, prunes the clone pool and maintains the database

    pool
        {clone.cfg : The configuration file of the clone}
    """

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self):
        """
        Executes the command.
        """
        self._io.title('Maintaining Clone Pool and Pool Metadata')

        helper = PoolSync(self._io)
        helper.synchronize()

        DataLayer.instance.commit()

# ----------------------------------------------------------------------------------------------------------------------
