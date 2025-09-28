from cleo.application import Application

from backuppc_clone.command.AutoCommand import AutoCommand
from backuppc_clone.command.BackupCloneCommand import BackupCloneCommand
from backuppc_clone.command.BackupDeleteCommand import BackupDeleteCommand
from backuppc_clone.command.BackupPreScanCommand import BackupPreScanCommand
from backuppc_clone.command.HostDeleteCommand import HostDeleteCommand
from backuppc_clone.command.InitCloneCommand import InitCloneCommand
from backuppc_clone.command.InitOriginalCommand import InitOriginalCommand
from backuppc_clone.command.NagiosCommand import NagiosCommand
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
        Application.__init__(self, 'backuppc-clone', '0.0.0')

        self.add(AutoCommand())
        self.add(BackupCloneCommand())
        self.add(BackupDeleteCommand())
        self.add(BackupPreScanCommand())
        self.add(HostDeleteCommand())
        self.add(InitCloneCommand())
        self.add(InitOriginalCommand())
        self.add(NagiosCommand())
        self.add(PoolCommand())
        self.add(SyncAuxiliaryCommand())
        self.add(TraversePerformanceTestCommand())
        self.add(VacuumCommand())

# ----------------------------------------------------------------------------------------------------------------------
