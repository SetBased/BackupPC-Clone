import os
import time
from pathlib import Path

from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.ProgressBar import ProgressBar
from backuppc_clone.helper.PoolScanner import PoolScanner
from backuppc_clone.CloneIO import CloneIO


class PoolSync:
    """
    Inventories the original pool, prunes the clone pool and maintains the database.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io: CloneIO):
        """
        Object constructor.

        @param io: The output style.
        """

        self.__io: CloneIO = io
        """
        The output style.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __clone_pool_remove_obsolete(self) -> None:
        """
        Removes obsolete files from pool of clone.
        """
        self.__io.write_line('')
        self.__io.sub_title('Clone pool')
        self.__io.write_line('')

        file_count = DataLayer.instance.clone_pool_obsolete_files_prepare()
        progress = ProgressBar(self.__io.output, file_count)

        top_dir_clone = Config.instance.top_clone_path
        count = 0
        for rows in DataLayer.instance.clone_pool_obsolete_files_yield():
            for row in rows:
                try:
                    path = os.path.join(top_dir_clone, row['bpl_dir'], row['bpl_name'])
                    self.__io.log_very_verbose(f'Removing <fso>{path}</fso>')
                    os.remove(path)
                    count += 1
                except FileNotFoundError:
                    # Nothing to do.
                    pass

                DataLayer.instance.pool_delete_row(row['bpl_id'])
                progress.advance()

        progress.finish()

        self.__io.write_line('')
        self.__io.write_line(f' Files removed: {count}')
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_original_pool(self, csv_path: Path) -> None:
        """
        Scans the pool of the original and stores the data into a CSV file.

        @param csv_path: The path to the CSV file.
        """
        self.__io.sub_title('Original pool')

        scanner = PoolScanner(self.__io)
        scanner.scan_directory(Config.instance.top_original_path, ['pool', 'cpool'], csv_path)

        self.__io.write_line(f' Files found: {scanner.count}')
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_clone_pool(self, csv_path: Path) -> None:
        """
        Scans the pool of the clone and stores the data into a CSV file.

        @param csv_path: The path to the CSV file.
        """
        self.__io.sub_title('Clone pool')

        scanner = PoolScanner(self.__io)
        scanner.scan_directory(Config.instance.top_clone_path, ['pool', 'cpool'], csv_path)

        self.__io.write_line(f' Files found: {scanner.count}')
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def __import_csv(self, csv_path: Path) -> None:
        """
        Imports to CSV file with entries of the original pool into the SQLite database.

        @param csv_path: The path to the CSV file.
        """
        self.__io.log_verbose(f' Importing <fso>{csv_path}</fso> into <dbo>IMP_POOL</dbo>')

        DataLayer.instance.import_csv('IMP_POOL', ['imp_inode', 'imp_dir', 'imp_name'], csv_path)

    # ------------------------------------------------------------------------------------------------------------------
    def __update_database_original(self) -> None:
        """
        Updates the database.
        """
        self.__io.write_line(' Updating <dbo>BKC_POOL</dbo>')
        self.__io.write_line('')

        DataLayer.instance.pool_delete_obsolete_original_rows()
        DataLayer.instance.pool_insert_new_original()

    # ------------------------------------------------------------------------------------------------------------------
    def __update_database_clone(self) -> None:
        """
        Updates the database.
        """
        self.__io.write_line(' Updating <dbo>BKC_POOL</dbo>')
        self.__io.write_line('')

        row_count = DataLayer.instance.clone_pool_delete_missing()

        self.__io.write_line(f' Rows removed: {row_count}')
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def synchronize(self) -> None:
        """
        Inventories the original pool, prunes the clone pool and maintains the database.
        """
        Config.instance.last_pool_scan = int(time.time())

        csv_path = Config.instance.tmp_clone_path.joinpath('pool.csv')

        self.__scan_clone_pool(csv_path)
        self.__import_csv(csv_path)
        self.__update_database_clone()

        self.__scan_original_pool(csv_path)
        self.__import_csv(csv_path)
        self.__clone_pool_remove_obsolete()
        self.__update_database_original()


# ----------------------------------------------------------------------------------------------------------------------
