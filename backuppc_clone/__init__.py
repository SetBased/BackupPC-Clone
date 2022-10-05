from backuppc_clone.application.BackupPcCloneApplication import BackupPcCloneApplication


def main() -> int:
    application = BackupPcCloneApplication()
    ret = application.run()

    return ret
