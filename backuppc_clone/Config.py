import configparser
import os
from pathlib import Path

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
    def __init__(self, config_filename: str):
        """
        Object constructor.

        @param str config_filename: The path to the configuration file of the clone.
        """
        if Config.instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Config.instance = self

        self.__config_filename: str = config_filename
        """
        The path to the configuration file of the clone.
        """

        self.__stats_filename: str | None = None
        """
        The path to the stats file.
        """

        self.__top_dir_clone: str | None = None
        """
        The top dir of the clone.
        """

        self.__tmp_dir_clone: str | None = None
        """
        The temp dir of the clone.
        """

        self.__top_dir_original: str | None = None
        """
        The top dir of the original.
        """

        self.__pc_dir_clone: str | None = None
        """
        The pc dir of the clone.
        """

        self.__pc_dir_original: Path | None = None
        """
        The pc dir of the original.
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def stats_file(self) -> str:
        """
        Returns the path to the stats file.

        :rtype: str
        """
        if self.__stats_filename is None:
            self.__stats_filename = os.path.join(os.path.dirname(self.__config_filename), 'status.json')

        return self.__stats_filename

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def last_pool_scan(self) -> int:
        """
        Returns the timestamp of the last original pool scan.

        :rtype: int
        """
        return int(DataLayer.instance.parameter_get_value('LAST_POOL_SYNC'))

    # ------------------------------------------------------------------------------------------------------------------
    @last_pool_scan.setter
    def last_pool_scan(self, value: int) -> None:
        """
        Saves the timestamp of the last original pool scan.

        @param int value: The timestamp.
        """
        DataLayer.instance.parameter_update_value('LAST_POOL_SYNC', str(value))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def pc_dir_clone(self) -> str:
        """
        Gives the pc dir of the clone.

        :rtype: str
        """
        if self.__pc_dir_clone is None:
            self.__pc_dir_clone = os.path.join(self.top_dir_clone, 'pc')

        return self.__pc_dir_clone

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def pc_dir_original(self) -> Path:
        """
        Gives the pc dir of the original.
        """
        if self.__pc_dir_original is None:
            config_clone = configparser.ConfigParser()
            config_clone.read(self.__config_filename)

            config_original = configparser.ConfigParser()
            config_original.read(config_clone['Original']['config'])

            self.__pc_dir_original = Path(config_original['Original']['pc_dir']).resolve(True)

        return self.__pc_dir_original

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def tmp_dir_clone(self) -> str:
        """
        Gives the temp dir of the clone.

        :rtype: str
        """
        if self.__tmp_dir_clone is None:
            self.__tmp_dir_clone = os.path.join(self.top_dir_clone, 'tmp')

        return self.__tmp_dir_clone

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def top_dir_clone(self) -> str:
        """
        Gives the top dir of the clone.

        :rtype: str
        """
        if self.__top_dir_clone is None:
            self.__top_dir_clone = os.path.realpath(os.path.dirname(self.__config_filename))

        return self.__top_dir_clone

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def top_dir_original(self) -> str:
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
    def backup_dir_clone(self, host: str, backup_no: int) -> str:
        """
        Returns the path to a host backup of the clone.

        @param str host: The name of the host.
        @param int backup_no: The backup number.

        :rtype: str
        """
        return os.path.join(self.top_dir_clone, 'pc', host, str(backup_no))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_dir_original(self, host: str, backup_no: int) -> str:
        """
        Returns the path to a host backup of the original.

        @param str host: The name of the host.
        @param int backup_no: The backup number.

        :rtype: str
        """
        return os.path.join(self.pc_dir_original, host, str(backup_no))

    # ------------------------------------------------------------------------------------------------------------------
    def host_dir_clone(self, host: str) -> str:
        """
        Returns the path to host of the clone.

        @param str host: The name of the host.

        :rtype: str
        """
        return os.path.join(self.top_dir_clone, 'pc', host)

    # ------------------------------------------------------------------------------------------------------------------
    def host_dir_original(self, host: str) -> str:
        """
        Returns the path to host of the original.

        @param str host: The name of the host.

        :rtype: str
        """
        return os.path.join(self.top_dir_original, 'pc', host)

# ----------------------------------------------------------------------------------------------------------------------
