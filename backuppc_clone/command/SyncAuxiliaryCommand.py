from cleo.helpers import argument

from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.helper.AuxiliaryFiles import AuxiliaryFiles


class SyncAuxiliaryCommand(BaseCommand):
    """
    Synchronizes the auxiliary files of the clone with the original.
    """
    name = 'sync-auxiliary'
    description = 'Synchronizes the auxiliary files of the clone with the original.'
    arguments = [argument(name='clone.cfg', description='The configuration file of the clone.')]

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self) -> None:
        """
        Executes the command.
        """
        self._io.title('Synchronizing Auxiliary Files')

        helper = AuxiliaryFiles(self._io)
        helper.synchronize()

        DataLayer.instance.commit()

# ----------------------------------------------------------------------------------------------------------------------
