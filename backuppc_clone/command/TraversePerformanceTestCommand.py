import os
import time

from cleo.commands.command import Command
from cleo.helpers import argument, option
from cleo.io.io import IO

from backuppc_clone.CloneIO import CloneIO


class TraversePerformanceTestCommand(Command):
    """
    Traversing recursively a directory performance test.
    """
    name = 'traverse-performance-test'
    description = 'Traversing recursively a directory performance test.'
    arguments = [argument(name='dir', description='The start directory.')]
    options = [option(long_name='stat', description='Get status of each file.')]

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Object constructor.
        """
        Command.__init__(self)

        self.__stat: bool = False
        """
        If True stat must be called for each file.
        """

        self._io: CloneIO | None = None
        """
        The output style.
        """

        self.__dir_count: int = 0
        """
        The number of directories counted.
        """

        self.__file_count: int = 0
        """
        The number of file counted.
        """

        self.__start_time: float = 0
        """
        The timestamp of the start of the performance test.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __traverse(self, path: str) -> None:
        """
        Traverse recursively a directory.

        @param str path: The path to the directory.
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
    def __report(self, end_time: float) -> None:
        """
        Prints the performance report.

        @param float end_time: The timestamp of the end of the performance test.
        """
        self._io.write_line('')
        self._io.write_line('number of directories: {}'.format(self.__dir_count))
        self._io.write_line('number of files      : {}'.format(self.__file_count))
        self._io.write_line('get status           : {}'.format('yes' if self.__stat else 'no'))
        self._io.write_line('duration             : {0:.1f}s'.format(end_time - self.__start_time))

    # ------------------------------------------------------------------------------------------------------------------
    def execute(self, io: IO) -> int:
        """
        Executes this command.

        :param io: The input/output object.
        """
        self._io = CloneIO(io.input, io.output, io.error_output)

        return self.handle()

    # ------------------------------------------------------------------------------------------------------------------
    def handle(self) -> int:
        """
        Executes the command.
        """
        self.__stat = self.option('stat')
        self.__dir_count = 0
        self.__file_count = 0
        self.__start_time = time.time()

        dir_name = self.argument('dir')

        self._io.write_line('Traversing <fso>{}</fso>'.format(dir_name))
        self.__traverse(dir_name)
        self.__report(time.time())

        return 0

# ----------------------------------------------------------------------------------------------------------------------
