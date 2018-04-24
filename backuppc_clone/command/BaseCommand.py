"""
BackupPC Clone
"""
import abc
import configparser
import os

from cleo import Command

from backuppc_clone.Config import Config
from backuppc_clone.DataLayer import DataLayer
from backuppc_clone.exception.BackupPcCloneException import BackupPcCloneException
from backuppc_clone.style.BackupPcCloneStyle import BackupPcCloneStyle


class BaseCommand(Command, metaclass=abc.ABCMeta):
    """
    Abstract parent command for (almost) all BackupPC Clone commands.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, name=None):
        """
        Object constructor.
        """
        Command.__init__(self, name)

        self._io = None
        """
        The output style.

        :type: backuppc_clone.style.BackupPcCloneStyle.BackupPcCloneStyle|None
        """

    # ------------------------------------------------------------------------------------------------------------------
    def __validate_user(self):
        """
        Validates that this command is not run under root.
        """
        self._io.log_very_verbose('testing user')

        if os.getuid() == 0:
            raise BackupPcCloneException('Will not run this command under root')

    # ------------------------------------------------------------------------------------------------------------------
    def __validate_config(self):
        """
        Validates the configuration files.
        """
        if self.input.has_argument('clone.cfg'):
            self._io.log_very_verbose('validation configuration')

            config_filename_clone = self.input.get_argument('clone.cfg')
            config_clone = configparser.ConfigParser()
            config_clone.read(config_filename_clone)

            config_original = configparser.ConfigParser()
            config_original.read(config_clone['Original']['config'])

            if config_clone['Original']['name'] != config_original['BackupPC Clone']['name']:
                raise BackupPcCloneException(
                    'Clone {} is not a clone of original {}'.format(config_clone['Original']['name'],
                                                                    config_original['BackupPC Clone']['name']))

    # ------------------------------------------------------------------------------------------------------------------
    def ask(self, question, default=None):
        """
        Prompt the user for input.

        :param str question: The question to ask
        :param str|None default: The default value

        :rtype: str|None
        """
        if default is not None:
            question = question + ' [' + default + ']'

        answer = self._io.ask(question, default)
        if answer is None:
            answer = default

        return answer

    # ------------------------------------------------------------------------------------------------------------------
    def _init_singletons(self):
        """
        Initializes the singleton objects.
        """
        Config(self.argument('clone.cfg'))
        DataLayer(os.path.join(Config.instance.top_dir_clone, 'clone.db'))

    # ------------------------------------------------------------------------------------------------------------------
    @abc.abstractmethod
    def _handle_command(self):
        """
        Executes the command.

        :rtype: int
        """
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    def handle(self):
        """
        Executes the command.
        """
        try:
            self._io = BackupPcCloneStyle(self.input, self.output)

            self.__validate_user()
            self.__validate_config()
            self._init_singletons()

            return self._handle_command()

        except BackupPcCloneException as error:
            self._io.error(str(error))
            return -1

# ----------------------------------------------------------------------------------------------------------------------
