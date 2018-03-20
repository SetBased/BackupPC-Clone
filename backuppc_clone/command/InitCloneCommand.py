"""
BackupPC Clone
"""
import configparser
import os
import sqlite3

from backuppc_clone.command.BaseCommand import BaseCommand
from backuppc_clone.exception.BackupPcCloneException import BackupPcCloneException


class InitCloneCommand(BaseCommand):
    """
    Creates the configuration file for a clone

    init-clone
    """
    parameters = [('SCHEMA_VERSION', 'schema version', '1'),
                  ('LAST_POOL_SYNC', 'timestamp of last original pool scan', '-1')]

    # ------------------------------------------------------------------------------------------------------------------
    def __create_dirs(self, top_dir_clone):
        """
        Creates required directories under the top dir of the clone.

        :param str top_dir_clone: The top directory of the clone.
        """
        os.chmod(top_dir_clone, 0o770)

        self._io.writeln(' Creating directories')

        dir_names = ['cpool', 'pool', 'etc', 'pc', 'tmp', 'trash']
        for dir_name in dir_names:
            path = os.path.join(top_dir_clone, dir_name)
            if not os.path.isdir(path):
                self._io.log_verbose('Creating directory <fso>{}</fso>'.format(dir_name))
                os.mkdir(path, 0o700)

    # ------------------------------------------------------------------------------------------------------------------
    def __create_database(self, db_path):
        """
        Creates the metadata database.

        :param str db_path: The path to the SQLite database.
        """
        sql_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                '..',
                                'lib',
                                'ddl',
                                '0100_create_tables.sql')
        with open(sql_path) as file:
            sql = file.read()

        self._io.section('Creating metadata database')

        self._io.writeln(' Initializing <fso>{}</fso>'.format(db_path))
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.executescript(sql)

        for parameter in self.parameters:
            cursor.execute('insert into BKC_PARAMETER(prm_code, prm_description, prm_value) values(?, ?, ?)',
                           parameter)

        connection.commit()
        connection.close()

    # ------------------------------------------------------------------------------------------------------------------
    def __writing_config_clone(self, config_filename_clone, config_filename_original, name_clone, name_master):
        """
        Creates the config file for the clone.

        :param str config_filename_clone: The path to the config file of the clone.
        :param str config_filename_original: The path to the config file of the original.
        :param str name_clone: The name of the clone.
        :param str name_master: The name of the master.
        """
        self._io.writeln(' Writing <fso>{}</fso>'.format(config_filename_clone))

        config = configparser.ConfigParser()
        config['BackupPC Clone'] = {'role': 'clone',
                                    'name': name_clone}
        config['Original'] = {'config': config_filename_original,
                              'name':   name_master}
        with open(config_filename_clone, 'w') as config_file:
            config.write(config_file)

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
        self._io.title('Initializing Clone')

        self._io.section('Creating configuration file')

        top_dir_original = self.ask('top dir of the original', '/var/lib/BackupPC')
        config_filename_original = os.path.join(top_dir_original, 'original.cfg')

        if not os.path.isfile(config_filename_original):
            raise BackupPcCloneException(
                'Configuration file <fso>{}</fso> of original not found'.format(config_filename_original))

        config_original = configparser.ConfigParser()
        config_original.read(config_filename_original)

        top_dir_clone = None
        while top_dir_clone is None or not os.path.isdir(top_dir_clone):
            top_dir_clone = self.ask('top dir of the clone')

        name_clone = self.ask('name of clone', config_original['BackupPC Clone']['name'] + '-clone')

        config_filename_clone = os.path.join(top_dir_clone, 'clone.cfg')

        if os.path.isfile(config_filename_clone):
            create = self.confirm('Overwrite {}'.format(config_filename_clone), False)
        else:
            create = True

        if create:
            self.__writing_config_clone(config_filename_clone,
                                        config_filename_original,
                                        name_clone,
                                        config_original['BackupPC Clone']['name'])

            self.__create_dirs(top_dir_clone)

            self._io.writeln('')

            self.__create_database(os.path.join(top_dir_clone, 'clone.db'))
        else:
            self._io.warning('No configuration file created')

# ----------------------------------------------------------------------------------------------------------------------
