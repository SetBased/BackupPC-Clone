"""
BackupPC Clone
"""
from cleo import Application

from backuppc_clone.command.AutoCommand import AutoCommand
from backuppc_clone.command.BackupCloneCommand import BackupCloneCommand
from backuppc_clone.command.BackupDeleteCommand import BackupDeleteCommand
from backuppc_clone.command.BackupPreScanCommand import BackupPreScanCommand
from backuppc_clone.command.HostDeleteCommand import HostDeleteCommand
from backuppc_clone.command.InitCloneCommand import InitCloneCommand
from backuppc_clone.command.InitOriginalCommand import InitOriginalCommand
from backuppc_clone.command.PoolCommand import PoolCommand
from backuppc_clone.command.SyncAuxiliaryCommand import SyncAuxiliaryCommand
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
        Application.__init__(self, 'backuppc-clone', '1.0.0')

    # ------------------------------------------------------------------------------------------------------------------
    def get_default_commands(self):
        """
        Returns the default commands of this application.

        :rtype: list[cleo.Command]
        """
        commands = Application.get_default_commands(self)

        commands.append(AutoCommand())
        commands.append(BackupCloneCommand())
        commands.append(BackupDeleteCommand())
        commands.append(BackupPreScanCommand())
        commands.append(HostDeleteCommand())
        commands.append(InitCloneCommand())
        commands.append(InitOriginalCommand())
        commands.append(PoolCommand())
        commands.append(SyncAuxiliaryCommand())
        commands.append(TraversePerformanceTestCommand())
        commands.append(VacuumCommand())

        return commands

# ----------------------------------------------------------------------------------------------------------------------
