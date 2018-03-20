"""
BackupPC Clone
"""
from backuppc_clone.application.BackupPcCloneApplication import BackupPcCloneApplication


def main():
    application = BackupPcCloneApplication()
    ret = application.run()

    return ret
