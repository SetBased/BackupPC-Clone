"""
BackupPC Clone
"""
import os
import time

from cleo import Command

from backuppc_clone.style.BackupPcCloneStyle import BackupPcCloneStyle


class TraversePerformanceTestCommand(Command):
    """
    Traversing recursively a directory performance test

    traverse-performance-test
        {--stat : Get status of each file}
        {dir    : The start directory}
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        Command.__init__(self)

        self.__stat = False
        """
        If True stat must be called for each file.

        :type: bool
        """

        self._io = None
        """
        The output style.

        :type: backuppc_clone.style.BackupPcCloneStyle.BackupPcCloneStyleG57G
        """

        self.__dir_count = 0
        """
        The number of directories counted.

        :type: int
        """

        self.__file_count = 0
        """
        The number of file counted.

        :type: int
        """

        self.__start_time = 0
        """
        The timestamp of the start of the performance test.

        :type: int
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __traverse(self, path):
        """
        Traverse recursively a directory.

        :param str path: The path to the directory.
        """
        dirs = []
        for entry in os.scandir(path):
            if self.__stat and not entry.is_symlink():
                entry.stat()

            if entry.is_file():
                self.__file_count += 1

            elif entry.is_dir():
                dirs.append(entry.name)
                self.__dir_count += 1

        for name in dirs:
            self.__traverse(os.path.join(path, name))

    # ------------------------------------------------------------------------------------------------------------------
    def __report(self, end_time):
        """
        Prints the performance report.

        :param int end_time: The timestamp of the end of the performance test.
        """
        self._io.writeln('')
        self._io.writeln('number of directories: {}'.format(self.__dir_count))
        self._io.writeln('number of files      : {}'.format(self.__file_count))
        self._io.writeln('get status           : {}'.format('yes' if self.__stat else 'no'))
        self._io.writeln('duration             : {0:.1f}s'.format(end_time - self.__start_time))

    # ------------------------------------------------------------------------------------------------------------------
    def execute(self, i, o):
        """
        Executes the command.

        :param cleo.inputs.input.Input i: The input.
        :param cleo.outputs.output.Output o: The output.

        :rtype: int
        """
        self.input = i
        self.output = o

        return self.handle()

    # ------------------------------------------------------------------------------------------------------------------
    def handle(self):
        """
        Executes the command.
        """
        self._io = BackupPcCloneStyle(self.input, self.output)

        self.__stat = self.option('stat')
        self.__dir_count = 0
        self.__file_count = 0
        self.__start_time = time.time()

        dir_name = self.argument('dir')

        self._io.writeln('Traversing <fso>{}</fso>'.format(dir_name))
        self.__traverse(dir_name)
        self.__report(time.time())

# ----------------------------------------------------------------------------------------------------------------------
