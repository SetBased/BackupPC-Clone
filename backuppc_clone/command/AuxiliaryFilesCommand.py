"""
BackupPC Clone
"""
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.helper.AuxiliaryFiles import AuxiliaryFiles


class AuxiliaryFilesCommand(BaseCommand):
    """
    Copies auxiliary files from original to clone.

    auxiliary-files
        {clone.cfg : The configuration file of the clone}
    """

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self):
        """
        Executes the command.
        """
        self._io.title('Synchronizing Auxiliary Files')

        helper = AuxiliaryFiles(self._io)
        helper.synchronize()

        DataLayer.instance.commit()

# ----------------------------------------------------------------------------------------------------------------------
