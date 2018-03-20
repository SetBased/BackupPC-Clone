"""
BackupPC Clone
"""
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand


class VacuumCommand(BaseCommand):
    """
    Rebuilds the SQLite database freeing disk space.

    vacuum
        {clone.cfg : The configuration file of the clone}
    """

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self):
        """
        Executes the command.
        """
        DataLayer.instance.vacuum()

# ----------------------------------------------------------------------------------------------------------------------
