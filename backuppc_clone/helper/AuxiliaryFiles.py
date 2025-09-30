import os
import shutil
from typing import List

from backuppc_clone.Config import Config
from backuppc_clone.helper.AuxiliaryFileScanner import AuxiliaryFileScanner
from backuppc_clone.misc import sizeof_fmt
from backuppc_clone.CloneIO import CloneIO


class AuxiliaryFiles:
    """
    Copies auxiliary files from original to clone.
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

    # ------------------------------------------------------------------------------------------------------------------
    def __remove_obsolete_files(self, files_original: List, files_clone: List) -> None:
        """
        Removes obsolete auxiliary files of the Clone.

        @param list files_original: The metadata of the auxiliary files of the Original.
        @param list files_clone: The metadata of the auxiliary files of the Clone.
        """
        self.__io.sub_title('Removing obsolete and changed files')

        obsolete = []
        for file in files_clone:
            if file not in files_original:
                obsolete.append(file)

        total_size = 0
        file_count = 0
        for file in obsolete:
            path = os.path.join(Config.instance.top_dir_clone, 'pc', file['host'], file['name'])
            self.__io.log_very_verbose(f'Removing <fso>{path}</fso>')
            os.unlink(path)
            file_count += 1
            total_size += file['size']

        self.__io.write_line(f' Number of files removed: {file_count}')
        self.__io.write_line(f' Total bytes freed      : {sizeof_fmt(total_size)} ({total_size}B) ')
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def __copy_new_files(self, files_original: List, files_clone: List) -> None:
        """
        Copies new auxiliary files from the Original to Clone.

        @param list files_original: The metadata of the auxiliary files of the Original.
        @param list files_clone: The metadata of the auxiliary files of the Clone.
        """
        self.__io.sub_title('Coping new and changed files')

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

            self.__io.log_very_verbose(f'Coping <fso>{path_original}</fso> to <fso>{path_clone}</fso>')

            if not os.path.exists(host_dir_clone):
                os.makedirs(host_dir_clone)

            shutil.copy2(path_original, path_clone)

            file_count += 1
            total_size += file['size']

        self.__io.write_line(f' Number of files copied: {file_count}')
        self.__io.write_line(f' Total bytes copied    : {sizeof_fmt(total_size)} ({total_size}B) ')
        self.__io.write_line('')

    # ------------------------------------------------------------------------------------------------------------------
    def synchronize(self) -> None:
        """
        Synchronizes the auxiliary file sof the Clone with the auxiliary files of the Original.
        """
        scanner = AuxiliaryFileScanner(self.__io)
        files_original = scanner.scan(Config.instance.pc_dir_original)
        files_clone = scanner.scan(Config.instance.pc_dir_clone)

        self.__io.write_line('')

        self.__remove_obsolete_files(files_original, files_clone)
        self.__copy_new_files(files_original, files_clone)

# ----------------------------------------------------------------------------------------------------------------------
