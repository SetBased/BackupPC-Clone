"""
BackupPC Clone
"""
import os
import shutil

from backuppc_clone.Config import Config
from backuppc_clone.helper.AuxiliaryFileScanner import AuxiliaryFileScanner
from backuppc_clone.misc import sizeof_fmt


class AuxiliaryFiles:
    """
    Copies auxiliary files from original to clone.
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

    # ------------------------------------------------------------------------------------------------------------------
    def __remove_obsolete_files(self, files_original, files_clone):
        """
        Removes obsolete auxiliary files of the Clone.

        :param list files_original: The metadata of the auxiliary files of the Original.
        :param list files_clone: The metadata of the auxiliary files of the Clone.
        """
        self.__io.section('Removing obsolete and changed files')

        obsolete = []
        for file in files_clone:
            if file not in files_original:
                obsolete.append(file)

        total_size = 0
        file_count = 0
        for file in obsolete:
            path = os.path.join(Config.instance.top_dir_clone, 'pc', file['host'], file['name'])
            self.__io.log_very_verbose('Removing <fso>{}</fso>'.format(path))
            os.unlink(path)
            file_count += 1
            total_size += file['size']

        self.__io.writeln(' Number of files removed: {}'.format(file_count))
        self.__io.writeln(' Total bytes freed      : {} ({}B) '.format(sizeof_fmt(total_size), total_size))
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def __copy_new_files(self, files_original, files_clone):
        """
        Copies new auxiliary files from the Original to Clone.

        :param list files_original: The metadata of the auxiliary files of the Original.
        :param list files_clone: The metadata of the auxiliary files of the Clone.
        """
        self.__io.section('Coping new and changed files')

        new = []
        for file in files_original:
            if file not in files_clone:
                new.append(file)

        total_size = 0
        file_count = 0
        for file in new:
            host_dir_clone = Config.instance.host_dir_clone(file['host'])
            host_dir_original = Config.instance.host_dir_original(file['host'])

            path_clone = os.path.join(host_dir_clone, file['name'])
            path_original = os.path.join(host_dir_original, file['name'])

            self.__io.log_very_verbose('Coping <fso>{}</fso> to <fso>{}</fso>'.format(path_original, path_clone))

            if not os.path.exists(host_dir_clone):
                os.makedirs(host_dir_clone)

            shutil.copy2(path_original, path_clone)

            file_count += 1
            total_size += file['size']

        self.__io.writeln(' Number of files copied: {}'.format(file_count))
        self.__io.writeln(' Total bytes copied    : {} ({}B) '.format(sizeof_fmt(total_size), total_size))
        self.__io.writeln('')

    # ------------------------------------------------------------------------------------------------------------------
    def synchronize(self):
        """
        Synchronizes the auxiliary file sof the Clone with the auxiliary files of the Original.
        """
        scanner = AuxiliaryFileScanner(self.__io)
        files_original = scanner.scan(Config.instance.pc_dir_original)
        files_clone = scanner.scan(Config.instance.pc_dir_clone)

        self.__io.writeln('')

        self.__remove_obsolete_files(files_original, files_clone)
        self.__copy_new_files(files_original, files_clone)

# ----------------------------------------------------------------------------------------------------------------------
