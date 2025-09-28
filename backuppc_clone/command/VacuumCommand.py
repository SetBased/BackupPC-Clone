from cleo.helpers import argument

from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.command.BaseCommand import BaseCommand


class VacuumCommand(BaseCommand):
    """
    Rebuilds the SQLite database freeing disk space.
    """
    name = 'vacuum'
    description = 'Rebuilds the SQLite database freeing disk space.'
    arguments = [argument(name='clone.cfg', description='The configuration file of the clone.')]

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self) -> None:
        """
        Executes the command.
        """
        DataLayer.instance.vacuum()

# ----------------------------------------------------------------------------------------------------------------------
