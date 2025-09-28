import os
import shutil
from pathlib import Path

from backuppc_clone.CloneIO import CloneIO
from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.helper.BackupScanner import BackupScanner
from backuppc_clone.misc import sizeof_fmt
from backuppc_clone.ProgressBar import ProgressBar


class BackupClone:
    """
    Clones a backup of a host
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io: CloneIO):
        """
        Object constructor.

        @param CloneIO io: The output style.
        """

        self.__io: CloneIO = io
        """
        The output style.
        """

        self.__host: str = ''
        """
        The host of the backup.
        """

        self.__backup_no: int = 0
        """
        The number of the backup.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_host_backup(self, csv_path: Path) -> None:
        """
        Scans the backup of a host.

        @param csv_path: The path to the CSV file.
        """
        self.__io.sub_title('Original backup')

        scanner = BackupScanner(self.__io)
        scanner.scan_directory(self.__host, self.__backup_no, csv_path)

        self.__io.write_line('')
        self.__io.write_line(f' Files found:       {scanner.file_count}')
        self.__io.write_line(f' Directories found: {scanner.dir_count}')
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def __import_host_scan_csv(self, csv_path: Path) -> None:
        """
        Imports to CSV file with entries of the original pool into the SQLite database.

        @param csv_path: The path to the CSV file.
        """
        self.__io.log_very_verbose(f' Importing <fso>{csv_path}</fso>')

        hst_id = DataLayer.instance.get_host_id(self.__host)
        bck_id = DataLayer.instance.get_bck_id(hst_id, int(self.__backup_no))

        DataLayer.instance.backup_empty(bck_id)
        DataLayer.instance.import_csv('BKC_BACKUP_TREE',
                                      ['bbt_seq', 'bbt_inode_original', 'bbt_dir', 'bbt_name'],
                                      csv_path,
                                      False,
                                      {'bck_id': bck_id})

    # ------------------------------------------------------------------------------------------------------------------
    def __import_pre_scan_csv(self, csv_path: Path) -> None:
        """
        Imports to CSV file with entries of the original pool into the SQLite database.

        @param csv_path: The path to the CSV file.
        """
        self.__io.sub_title('Using pre-scan')

        self.__import_host_scan_csv(csv_path)

        hst_id = DataLayer.instance.get_host_id(self.__host)
        bck_id = DataLayer.instance.get_bck_id(hst_id, int(self.__backup_no))

        stats = DataLayer.instance.backup_get_stats(bck_id)

        self.__io.write_line(f" Files found:       {stats['#files']}")
        self.__io.write_line(f" Directories found: {stats['#dirs']}")
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def __copy_pool_file(self, dir_name: str, file_name: str, bpl_inode_original: int) -> int:
        """
        Copies a pool file from the Original pool to the clone pool. Returns the size of the file.

        @param str dir_name: The directory name relative to the top dir.
        @param str file_name: The file name.
        @param int bpl_inode_original: The inode of the original pool file.

        :rtype: int
        """
        original_path = os.path.join(Config.instance.top_original_path, dir_name, file_name)
        clone_dir = Config.instance.top_clone_path.joinpath(dir_name)
        clone_path = clone_dir.joinpath(file_name)

        self.__io.log_very_verbose(f'Coping <fso>{original_path}</fso> to <fso>{clone_dir}</fso>')

        stats_original = os.stat(original_path)
        if stats_original.st_ino != bpl_inode_original:
            raise FileNotFoundError(f"Filename '{original_path}' and inode {bpl_inode_original} do not match")

        if not os.path.exists(clone_dir):
            os.makedirs(clone_dir)

        shutil.copy(original_path, clone_path)

        stats_clone = os.stat(clone_path)
        os.chmod(clone_path, stats_original.st_mode)
        os.utime(clone_path, (stats_original.st_mtime, stats_original.st_mtime))

        DataLayer.instance.pool_update_by_inode_original(stats_original.st_ino,
                                                         stats_clone.st_ino,
                                                         stats_original.st_size,
                                                         stats_original.st_mtime)

        return stats_original.st_size

    # ------------------------------------------------------------------------------------------------------------------
    def __update_clone_pool(self) -> None:
        """
        Copies required pool files from the original pool to the clone pool.
        """
        self.__io.sub_title('Clone pool')
        self.__io.write_line(' Adding files ...')
        self.__io.write_line('')

        hst_id = DataLayer.instance.get_host_id(self.__host)
        bck_id = DataLayer.instance.get_bck_id(hst_id, self.__backup_no)

        file_count = DataLayer.instance.backup_prepare_required_clone_pool_files(bck_id)
        progress = ProgressBar(self.__io.output, file_count)

        total_size = 0
        file_count = 0
        for rows in DataLayer.instance.backup_yield_required_clone_pool_files():
            for row in rows:
                total_size += self.__copy_pool_file(row['bpl_dir'], row['bpl_name'], row['bpl_inode_original'])
                file_count += 1
                progress.advance()

        progress.finish()

        self.__io.write_line('')
        self.__io.write_line(f' Number of files copied: {file_count}')
        self.__io.write_line(f' Total bytes copied    : {sizeof_fmt(total_size)} ({total_size}B)')
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def __clone_backup(self) -> None:
        """
        Clones the backup.
        """
        self.__io.sub_title('Clone backup')
        self.__io.write_line(' Populating ...')
        self.__io.write_line('')

        hst_id = DataLayer.instance.get_host_id(self.__host)
        bck_id = DataLayer.instance.get_bck_id(hst_id, int(self.__backup_no))
        DataLayer.instance.backup_set_in_progress(bck_id, 1)

        backup_clone_path = Config.instance.backup_clone_path(self.__host, self.__backup_no)
        if backup_clone_path.exists():
            shutil.rmtree(backup_clone_path)
        backup_clone_path.mkdir(parents=True, exist_ok=True)

        backup_original_path = Config.instance.backup_original_path(self.__host, self.__backup_no)
        top_clone_path = Config.instance.top_clone_path

        file_count = DataLayer.instance.backup_prepare_tree(bck_id)
        progress = ProgressBar(self.__io.output, file_count)

        file_count = 0
        link_count = 0
        dir_count = 0
        for rows in DataLayer.instance.backup_yield_tree():
            for row in rows:
                if row['bbt_dir'] is None:
                    row['bbt_dir'] = ''

                target_clone = os.path.join(backup_clone_path, row['bbt_dir'], row['bbt_name'])

                if row['bpl_inode_original']:
                    # Entry is a file linked to the pool.
                    source_clone = os.path.join(top_clone_path, row['bpl_dir'], row['bpl_name'])
                    self.__io.log_very_verbose(f'Linking to <fso>{source_clone}</fso> from <fso>{target_clone}</fso>')
                    os.link(source_clone, target_clone)
                    link_count += 1

                elif row['bbt_inode_original']:
                    # Entry is a file not linked to the pool.
                    source_original = os.path.join(backup_original_path, row['bbt_dir'], row['bbt_name'])
                    self.__io.log_very_verbose(f'Copying <fso>{source_original}</fso> to <fso>{target_clone}</fso>')
                    shutil.copy2(source_original, target_clone)
                    file_count += 1
                else:
                    # Entry is a directory
                    os.mkdir(target_clone)
                    dir_count += 1

                progress.advance()

        progress.finish()

        DataLayer.instance.backup_set_in_progress(bck_id, 0)

        self.__io.write_line('')
        self.__io.write_line(f' Number of files copied       : {file_count}')
        self.__io.write_line(f' Number of hardlinks created  : {link_count}')
        self.__io.write_line(f' Number of directories created: {dir_count}')
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def clone_backup(self, host: str, backup_no: int) -> None:
        """
        Clones a backup of a host.
        """

        self.__host = host
        self.__backup_no = backup_no

        backup_original_path = Config.instance.backup_original_path(host, backup_no)
        pre_scan_csv_path = backup_original_path.joinpath('backuppc-clone.csv')
        if os.path.isfile(pre_scan_csv_path):
            self.__import_pre_scan_csv(pre_scan_csv_path)
        else:
            csv_path = Config.instance.tmp_clone_path.joinpath(f'backup-{host}-{backup_no}.csv')
            self.__scan_host_backup(csv_path)
            self.__import_host_scan_csv(csv_path)

        self.__update_clone_pool()
        self.__clone_backup()

# ----------------------------------------------------------------------------------------------------------------------
