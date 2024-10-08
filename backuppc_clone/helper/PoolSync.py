import os
import time

from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.ProgressBar import ProgressBar
from backuppc_clone.helper.PoolScanner import PoolScanner
from backuppc_clone.style.BackupPcCloneStyle import BackupPcCloneStyle


class PoolSync:
    """
    Inventories the original pool, prunes the clone pool and maintains the database.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io: BackupPcCloneStyle):
        """
        Object constructor.

        @param BackupPcCloneStyle io: The output style.
        """

        self.__io: BackupPcCloneStyle = io
        """
        The output style.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __clone_pool_remove_obsolete(self) -> None:
        """
        Removes obsolete files from pool of clone.
        """
        self.__io.writeln('')
        self.__io.section('Clone pool')
        self.__io.writeln('')

        file_count = DataLayer.instance.clone_pool_obsolete_files_prepare()
        progress = ProgressBar(self.__io.output, file_count)

        top_dir_clone = Config.instance.top_dir_clone
        count = 0
        for rows in DataLayer.instance.clone_pool_obsolete_files_yield():
            for row in rows:
                try:
                    path = os.path.join(top_dir_clone, row['bpl_dir'], row['bpl_name'])
                    self.__io.log_very_verbose('Removing <fso>{}</fso>'.format(path))
                    os.remove(path)
                    count += 1
                except FileNotFoundError:
                    # Nothing to do.
                    pass

                DataLayer.instance.pool_delete_row(row['bpl_id'])
                progress.advance()

        progress.finish()

        self.__io.writeln('')
        self.__io.writeln(' Files removed: {}'.format(count))
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_original_pool(self, csv_filename: str) -> None:
        """
        Scans the pool of the original and stores the data into a CSV file.

        @param str csv_filename: The name of the CSV file.
        """
        self.__io.section('Original pool')

        scanner = PoolScanner(self.__io)
        scanner.scan_directory(Config.instance.top_dir_original, ['pool', 'cpool'], csv_filename)

        self.__io.writeln(' Files found: {}'.format(scanner.count))
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_clone_pool(self, csv_filename: str) -> None:
        """
        Scans the pool of the clone and stores the data into a CSV file.

        @param str csv_filename: The name of the CSV file.
        """
        self.__io.section('Clone pool')

        scanner = PoolScanner(self.__io)
        scanner.scan_directory(Config.instance.top_dir_clone, ['pool', 'cpool'], csv_filename)

        self.__io.writeln(' Files found: {}'.format(scanner.count))
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def __import_csv(self, csv_filename: str) -> None:
        """
        Imports to CSV file with entries of the original pool into the SQLite database.

        @param str csv_filename: The name of the CSV file.
        """
        self.__io.log_verbose(' Importing <fso>{}</fso> into <dbo>IMP_POOL</dbo>'.format(csv_filename))

        DataLayer.instance.import_csv('IMP_POOL', ['imp_inode', 'imp_dir', 'imp_name'], csv_filename)

    # ------------------------------------------------------------------------------------------------------------------
    def __update_database_original(self) -> None:
        """
        Updates the database.
        """
        self.__io.writeln(' Updating <dbo>BKC_POOL</dbo>')
        self.__io.writeln('')

        DataLayer.instance.pool_delete_obsolete_original_rows()
        DataLayer.instance.pool_insert_new_original()

    # ------------------------------------------------------------------------------------------------------------------
    def __update_database_clone(self) -> None:
        """
        Updates the database.
        """
        self.__io.writeln(' Updating <dbo>BKC_POOL</dbo>')
        self.__io.writeln('')

        row_count = DataLayer.instance.clone_pool_delete_missing()

        self.__io.writeln(' Rows removed: {}'.format(row_count))
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def synchronize(self) -> None:
        """
        Inventories the original pool, prunes the clone pool and maintains the database.
        """
        Config.instance.last_pool_scan = int(time.time())

        csv_filename = os.path.join(Config.instance.tmp_dir_clone, 'pool.csv')

        self.__scan_clone_pool(csv_filename)
        self.__import_csv(csv_filename)
        self.__update_database_clone()

        self.__scan_original_pool(csv_filename)
        self.__import_csv(csv_filename)
        self.__clone_pool_remove_obsolete()
        self.__update_database_original()


# ----------------------------------------------------------------------------------------------------------------------
