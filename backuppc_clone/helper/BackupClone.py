"""
BackupPC Clone
"""
import os
import shutil

from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.ProgressBar import ProgressBar
from backuppc_clone.helper.BackupScanner import BackupScanner
from backuppc_clone.misc import sizeof_fmt


class BackupClone:
    """
    Clones a backup of a host
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io):
        """
        Object constructor.

        :param backuppc_clone.style.BackupPcCloneStyle.BackupPcCloneStyle io: The output style.
        """

        self.__io = io
        """
        The output style.

        :type: backuppc_clone.style.BackupPcCloneStyle.BackupPcCloneStyle
        """

        self.__host = ''
        """
        The host of the backup.

        :type: str
        """

        self.__backup_no = 0
        """
        The number of the backup.

        :type: int
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __scan_host_backup(self, csv_filename):
        """
        Scans the backup of a host.

        :param str csv_filename: The name of the CSV file.
        """
        self.__io.section('Original backup')

        scanner = BackupScanner(self.__io)
        scanner.scan_directory(self.__host, self.__backup_no, csv_filename)

        self.__io.writeln('')
        self.__io.writeln(' Files found:       {}'.format(scanner.file_count))
        self.__io.writeln(' Directories found: {}'.format(scanner.dir_count))
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def __import_host_scan_csv(self, csv_filename):
        """
        Imports to CSV file with entries of the original pool into the SQLite database.

        :param str csv_filename: The name of the CSV file.
        """
        self.__io.log_very_verbose(' Importing <fso>{}</fso>'.format(csv_filename))

        hst_id = DataLayer.instance.get_host_id(self.__host)
        bck_id = DataLayer.instance.get_bck_id(hst_id, int(self.__backup_no))

        DataLayer.instance.backup_empty(bck_id)
        DataLayer.instance.import_csv('BKC_BACKUP_TREE',
                                      ['bbt_seq', 'bbt_inode_original', 'bbt_dir', 'bbt_name'],
                                      csv_filename,
                                      False,
                                      {'bck_id': bck_id})

    # ------------------------------------------------------------------------------------------------------------------
    def __import_pre_scan_csv(self, csv_filename):
        """
        Imports to CSV file with entries of the original pool into the SQLite database.

        :param str csv_filename: The name of the CSV file.
        """
        self.__io.section('Using pre-scan')

        self.__import_host_scan_csv(csv_filename)

        hst_id = DataLayer.instance.get_host_id(self.__host)
        bck_id = DataLayer.instance.get_bck_id(hst_id, int(self.__backup_no))

        stats = DataLayer.instance.backup_get_stats(bck_id)

        self.__io.writeln(' Files found:       {}'.format(stats['#files']))
        self.__io.writeln(' Directories found: {}'.format(stats['#dirs']))
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def __copy_pool_file(self, dir_name, file_name, bpl_inode_original):
        """
        Copies a pool file from the Original pool to the clone pool. Returns the size eof the file.

        :param str dir_name: The directory name relative to the top dir.
        :param str file_name: The file name.
        :param int bpl_inode_original: The inode of the original pool file.

        :rtype: int
        """
        original_path = os.path.join(Config.instance.top_dir_original, dir_name, file_name)
        clone_dir = os.path.join(Config.instance.top_dir_clone, dir_name)
        clone_path = os.path.join(clone_dir, file_name)

        self.__io.log_very_verbose('Coping <fso>{}</fso> to <fso>{}</fso>'.format(original_path, clone_dir))

        stats_original = os.stat(original_path)
        # BackupPC 3.x renames pool files with hash collisions.
        if stats_original.st_ino != bpl_inode_original:
            raise FileNotFoundError("Filename '{}' and inode {} do not match".format(original_path, bpl_inode_original))

        if not os.path.exists(clone_dir):
            os.makedirs(clone_dir)

        shutil.copyfile(original_path, clone_path)

        stats_clone = os.stat(clone_path)
        os.chmod(clone_path, stats_original.st_mode)
        os.utime(clone_path, (stats_original.st_mtime, stats_original.st_mtime))

        DataLayer.instance.pool_update_by_inode_original(stats_original.st_ino,
                                                         stats_clone.st_ino,
                                                         stats_original.st_size,
                                                         stats_original.st_mtime)

        return stats_original.st_size

    # ------------------------------------------------------------------------------------------------------------------
    def __update_clone_pool(self):
        """
        Copies required pool files from the original pool to the clone pool.
        """
        self.__io.section('Clone pool')
        self.__io.writeln(' Adding files ...')
        self.__io.writeln('')

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

        self.__io.writeln('')
        self.__io.writeln(' Number of files copied: {}'.format(file_count))
        self.__io.writeln(' Total bytes copied    : {} ({}B) '.format(sizeof_fmt(total_size), total_size))
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def __clone_backup(self):
        """
        Clones the backup.
        """
        self.__io.section('Clone backup')
        self.__io.writeln(' Populating ...')
        self.__io.writeln('')

        hst_id = DataLayer.instance.get_host_id(self.__host)
        bck_id = DataLayer.instance.get_bck_id(hst_id, int(self.__backup_no))
        DataLayer.instance.backup_set_in_progress(bck_id, 1)

        backup_dir_clone = Config.instance.backup_dir_clone(self.__host, self.__backup_no)
        if os.path.exists(backup_dir_clone):
            shutil.rmtree(backup_dir_clone)
        os.makedirs(backup_dir_clone)

        backup_dir_original = Config.instance.backup_dir_original(self.__host, self.__backup_no)
        top_dir_clone = Config.instance.top_dir_clone

        file_count = DataLayer.instance.backup_prepare_tree(bck_id)
        progress = ProgressBar(self.__io.output, file_count)

        file_count = 0
        link_count = 0
        dir_count = 0
        for rows in DataLayer.instance.backup_yield_tree():
            for row in rows:
                if row['bbt_dir'] is None:
                    row['bbt_dir'] = ''

                target_clone = os.path.join(backup_dir_clone, row['bbt_dir'], row['bbt_name'])

                if row['bpl_inode_original']:
                    # Entry is a file linked to the pool.
                    source_clone = os.path.join(top_dir_clone, row['bpl_dir'], row['bpl_name'])
                    self.__io.log_very_verbose(
                            'Linking to <fso>{}</fso> from <fso>{}</fso>'.format(source_clone, target_clone))
                    os.link(source_clone, target_clone)
                    link_count += 1

                elif row['bbt_inode_original']:
                    # Entry is a file not linked to the pool.
                    source_original = os.path.join(backup_dir_original, row['bbt_dir'], row['bbt_name'])
                    self.__io.log_very_verbose('Copying <fso>{}</fso> to <fso>{}</fso>'.format(source_original,
                                                                                               target_clone))
                    shutil.copy2(source_original, target_clone)
                    file_count += 1
                else:
                    # Entry is a directory
                    os.mkdir(target_clone)
                    dir_count += 1

                progress.advance()

        progress.finish()

        DataLayer.instance.backup_set_in_progress(bck_id, 0)

        self.__io.writeln('')
        self.__io.writeln(' Number of files copied       : {}'.format(file_count))
        self.__io.writeln(' Number of hardlinks created  : {}'.format(link_count))
        self.__io.writeln(' Number of directories created: {}'.format(dir_count))
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def clone_backup(self, host, backup_no):
        """
        Clones a backup of a host.
        """
        self.__host = host
        self.__backup_no = backup_no

        backup_dir_original = Config.instance.backup_dir_original(host, backup_no)
        pre_scan_csv_filename = os.path.join(backup_dir_original, 'backuppc-clone.csv')
        if os.path.isfile(pre_scan_csv_filename):
            self.__import_pre_scan_csv(pre_scan_csv_filename)
        else:
            csv_filename = os.path.join(Config.instance.tmp_dir_clone, 'backup-{}-{}.csv'.format(host, backup_no))
            self.__scan_host_backup(csv_filename)
            self.__import_host_scan_csv(csv_filename)

        self.__update_clone_pool()
        self.__clone_backup()

# ----------------------------------------------------------------------------------------------------------------------
