from cleo.helpers import argument

from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.helper.PoolSync import PoolSync


class PoolCommand(BaseCommand):
    """
    Inventories the original pool, prunes the clone pool and maintains the database.
    """
    name = 'pool'
    description = 'Inventories the original pool, prunes the clone pool and maintains the database.'
    arguments = [argument(name='clone.cfg', description='The configuration file of the clone.')]

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self) -> None:
        """
        Executes the command.
        """
        self._io.title('Maintaining Clone Pool and Pool Metadata')

        helper = PoolSync(self._io)
        helper.synchronize()

        DataLayer.instance.commit()

# ----------------------------------------------------------------------------------------------------------------------
