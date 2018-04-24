"""
BackupPC Clone
"""
import configparser
import os

from backuppc_clone.DataLayer import DataLayer


class Config:
    """
    Singleton class getting and updating parameters
    """
    instance = None
    """
    The singleton instance of this class.

    :type instance: backuppc_clone.Config.Config
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, config_filename):
        """
        Object constructor.

        :param str config_filename: The path to the configuration file of the clone.
        """
        if Config.instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Config.instance = self

        self.__config_filename = config_filename
        """
        The path to the configuration file of the clone.

        :type: str
        """

        self.__top_dir_clone = None
        """
        The top dir of the clone.

        :type: str|None
        """

        self.__tmp_dir_clone = None
        """
        The temp dir of the clone.

        :type: str|None
        """

        self.__top_dir_original = None
        """
        The top dir of the original.

        :type: str|None
        """

        self.__pc_dir_clone = None
        """
        The pc dir of the clone.

        :type: str|None
        """

        self.__pc_dir_original = None
        """
        The pc dir of the original.

        :type: str|None
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def last_pool_scan(self):
        """
        Returns the timestamp of the last original pool scan.

        :rtype: int
        """
        return int(DataLayer.instance.parameter_get_value('LAST_POOL_SYNC'))

    # ------------------------------------------------------------------------------------------------------------------
    @last_pool_scan.setter
    def last_pool_scan(self, value):
        """
        Saves the timestamp of the last original pool scan.

        :param int value: The timestamp.
        """
        DataLayer.instance.parameter_update_value('LAST_POOL_SYNC', str(value))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def pc_dir_clone(self):
        """
        Gives the pc dir of the clone.

        :rtype: str
        """
        if self.__pc_dir_clone is None:
            self.__pc_dir_clone = os.path.join(self.top_dir_clone, 'pc')

        return self.__pc_dir_clone

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def pc_dir_original(self):
        """
        Gives the pc dir of the original.

        :rtype: str
        """
        if self.__pc_dir_original is None:
            config_clone = configparser.ConfigParser()
            config_clone.read(self.__config_filename)

            config_original = configparser.ConfigParser()
            config_original.read(config_clone['Original']['config'])

            self.__pc_dir_original = os.path.realpath(config_original['Original']['pc_dir'])

        return self.__pc_dir_original

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def tmp_dir_clone(self):
        """
        Gives the temp dir of the clone.

        :rtype: str
        """
        if self.__tmp_dir_clone is None:
            self.__tmp_dir_clone = os.path.join(self.top_dir_clone, 'tmp')

        return self.__tmp_dir_clone

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def top_dir_clone(self):
        """
        Gives the top dir of the clone.

        :rtype: str
        """
        if self.__top_dir_clone is None:
            self.__top_dir_clone = os.path.realpath(os.path.dirname(self.__config_filename))

        return self.__top_dir_clone

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def top_dir_original(self):
        """
        Gives the top dir of the original.

        :rtype: str
        """
        if self.__top_dir_original is None:
            config_clone = configparser.ConfigParser()
            config_clone.read(self.__config_filename)

            self.__top_dir_original = os.path.realpath(os.path.dirname(config_clone['Original']['config']))

        return self.__top_dir_original

    # ------------------------------------------------------------------------------------------------------------------
    def backup_dir_clone(self, host, backup_no):
        """
        Returns the path to a host backup of the clone.

        :param str host: The name of the host.
        :param str|int backup_no: The backup number.

        :rtype: str
        """
        return os.path.join(self.top_dir_clone, 'pc', host, str(backup_no))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_dir_original(self, host, backup_no):
        """
        Returns the path to a host backup of the original.

        :param str host: The name of the host.
        :param str|int backup_no: The backup number.

        :rtype: str
        """
        return os.path.join(self.pc_dir_original, host, str(backup_no))

    # ------------------------------------------------------------------------------------------------------------------
    def host_dir_clone(self, host):
        """
        Returns the path to host of the clone.

        :param str host: The name of the host.

        :rtype: str
        """
        return os.path.join(self.top_dir_clone, 'pc', host)

    # ------------------------------------------------------------------------------------------------------------------
    def host_dir_original(self, host):
        """
        Returns the path to host of the original.

        :param str host: The name of the host.

        :rtype: str
        """
        return os.path.join(self.top_dir_original, 'pc', host)

# ----------------------------------------------------------------------------------------------------------------------
