"""
BackupPC Clone
"""
from cleo import Application

from backuppc_clone.command.AutoCommand import AutoCommand
from backuppc_clone.command.AuxiliaryFilesCommand import AuxiliaryFilesCommand
from backuppc_clone.command.CloneBackupCommand import CloneBackupCommand
from backuppc_clone.command.DeleteBackupCommand import DeleteBackupCommand
from backuppc_clone.command.DeleteHostCommand import DeleteHostCommand
from backuppc_clone.command.InitCloneCommand import InitCloneCommand
from backuppc_clone.command.InitOriginalCommand import InitOriginalCommand
from backuppc_clone.command.PoolCommand import PoolCommand
from backuppc_clone.command.PreScanBackupCommand import PreScanBackupCommand
from backuppc_clone.command.TraversePerformanceTestCommand import TraversePerformanceTestCommand
from backuppc_clone.command.VacuumCommand import VacuumCommand


class BackupPcCloneApplication(Application):
    """
    The BackupPC Clone application.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Object constructor
        """
        Application.__init__(self, 'backuppc-clone', '0.9.2')

    # ------------------------------------------------------------------------------------------------------------------
    def get_default_commands(self):
        """
        Returns the default commands of this application.

        :rtype: list[cleo.Command]
        """
        commands = Application.get_default_commands(self)

        commands.append(AutoCommand())
        commands.append(AuxiliaryFilesCommand())
        commands.append(CloneBackupCommand())
        commands.append(DeleteBackupCommand())
        commands.append(DeleteHostCommand())
        commands.append(InitCloneCommand())
        commands.append(InitOriginalCommand())
        commands.append(PoolCommand())
        commands.append(PreScanBackupCommand())
        commands.append(TraversePerformanceTestCommand())
        commands.append(VacuumCommand())

        return commands

# ----------------------------------------------------------------------------------------------------------------------
