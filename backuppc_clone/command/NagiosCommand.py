import json
import os
from pathlib import Path
from typing import Dict

from cleo.commands.command import Command
from cleo.helpers import argument

from backuppc_clone.Config import Config


class NagiosCommand(Command):
    """
    Performs a status check for Nagios.
    """
    name = 'nagios'
    description = 'Performs a status check for Nagios.'
    arguments = [argument(name='clone.cfg', description='The configuration file of the clone.')]

    # ------------------------------------------------------------------------------------------------------------------
    def __print_status(self, status: str, message: str, perf_data: str | None = None) -> None:
        """
        Prints the status of BackupPC Clone.
        """
        if perf_data:
            print(f'BackupPC Clone {status} - {message} | {perf_data}')
        else:
            print(f'BackupPC Clone {status} - {message}')

    # ------------------------------------------------------------------------------------------------------------------
    def __get_performance_data(self, stats: Dict[str, any]) -> str:
        """
        Returns the performance data string.

        @param dict stats: The stats of BackupPC Clone.

        :rtype: str
        """
        return f'backups={stats["n_backups"]} '\
               f'cloned_backups={stats["n_cloned_backups"]} '\
               f'not_cloned_backups={stats["n_not_cloned_backups"]} '\
               f'obsolete_cloned_backups={stats["n_obsolete_cloned_backups"]}'

    # ------------------------------------------------------------------------------------------------------------------
    def handle(self) -> int:
        """
        Executes the command.
        """
        config_filename_clone = self.argument('clone.cfg')
        if os.path.exists(config_filename_clone):
            config = Config(config_filename_clone)
            text = Path(config.stats_file).read_text()
            stats = json.loads(text)

            status = 'OK'
            message = 'Clone up to date'
            perf_data = self.__get_performance_data(stats)
            exit_status = 0
        else:
            status = 'ERROR'
            message = 'Clone not found'
            perf_data = None
            exit_status = 2

        self.__print_status(status, message, perf_data)

        return exit_status

# ----------------------------------------------------------------------------------------------------------------------
