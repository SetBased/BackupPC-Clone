"""
BackupPC Clone
"""
import configparser
import os
import subprocess

from backuppc_clone.command.BaseCommand import BaseCommand


class InitOriginalCommand(BaseCommand):
    """
    Creates the configuration file for the original

    init-original
    """

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __get_parameter(perl, backuppc_config_filename, parameter_name):
        """
        Extracts a parameter for BackupPCs configuration file.

        :param str perl: Path to the perl executable.
        :param str backuppc_config_filename: Path to BackupPC config file.
        :param parameter_name: The name of the parameter.

        :rtype: str
        """
        file = open(backuppc_config_filename, 'rt')
        code = file.read()

        code += '\n'
        code += 'print $Conf{{{}}};'.format(parameter_name)

        pipe = subprocess.Popen([perl], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        value = pipe.communicate(bytes(code, 'utf-8'))

        return str(value[0], 'utf-8')

    # ------------------------------------------------------------------------------------------------------------------
    def _init_singletons(self):
        """
        Omits the creating of singleton objects.
        """
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _handle_command(self):
        """
        Executes the command.
        """
        self._io.title('Creating Original Configuration File')

        while True:
            perl = self.ask('perl executable', '/usr/bin/perl')
            if os.path.isfile(perl):
                break

        while True:
            backuppc_config_filename = self.ask('Config file', '/etc/BackupPC/config.pl')
            if os.path.isfile(backuppc_config_filename):
                break

        name = self.__get_parameter(perl, backuppc_config_filename, 'ServerHost')
        top_dir = self.__get_parameter(perl, backuppc_config_filename, 'TopDir')
        conf_dir = self.__get_parameter(perl, backuppc_config_filename, 'ConfDir')
        log_dir = self.__get_parameter(perl, backuppc_config_filename, 'LogDir')
        pc_dir = os.path.join(top_dir, 'pc')

        config_filename_original = os.path.join(top_dir, 'original.cfg')

        if os.path.isfile(config_filename_original):
            create = self.confirm('Overwrite {}'.format(config_filename_original), False)
        else:
            create = True

        if create:
            self._io.writeln('Writing <fso>{}</fso>'.format(config_filename_original))

            config = configparser.ConfigParser()
            config['BackupPC Clone'] = {'role': 'original',
                                        'name': name}
            config['Original'] = {'top_dir':  top_dir,
                                  'conf_dir': conf_dir,
                                  'log_dir':  log_dir,
                                  'pc_dir':   pc_dir}
            with open(config_filename_original, 'w') as config_file:
                config.write(config_file)

        else:
            self._io.warning('No configuration file created')

# ----------------------------------------------------------------------------------------------------------------------
