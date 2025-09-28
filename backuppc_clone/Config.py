import configparser
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
    def __init__(self, config_path: Path):
        """
        Object constructor.

        @param str config_filename: The path to the configuration file of the clone.
        """
        if Config.instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Config.instance = self

        self.__config_path: Path = config_path.resolve()
        """
        The path to the configuration file of the clone.
        """

        self.__stats_filename: str | None = None
        """
        The path to the stats file.
        """

        self.__top_dir_clone: Path | None = None
        """
        The top dir of the clone.
        """

        self.__tmp_dir_clone: Path | None = None
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
    def stats_path(self) -> Path:
        """
        Returns the path to the stats file.
        """
        if self.__stats_filename is None:
            self.__stats_filename = self.__config_path.parent.joinpath('status.json')

        return self.__stats_filename

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def last_pool_scan(self) -> int:
        """
        Returns the timestamp of the last original pool scan.
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
    def pc_clone_path(self) -> Path:
        """
        Returns the path to the pc directory of the clone.
        """
        if self.__pc_dir_clone is None:
            self.__pc_dir_clone = self.top_clone_path.joinpath('pc')

        return self.__pc_dir_clone

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def pc_original_path(self) -> Path:
        """
        Returns the path to the pc directory of the original.
        """
        if self.__pc_dir_original is None:
            config_clone = configparser.ConfigParser()
            config_clone.read(self.__config_path)

            config_original = configparser.ConfigParser()
            config_original.read(config_clone['Original']['config'])

            self.__pc_dir_original = Path(config_original['Original']['pc_dir']).resolve(True)

        return self.__pc_dir_original

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def tmp_clone_path(self) -> Path:
        """
        Returns the path to temp directory of the clone.
        """
        if self.__tmp_dir_clone is None:
            self.__tmp_dir_clone = self.top_clone_path.joinpath('tmp')

        return self.__tmp_dir_clone

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def top_clone_path(self) -> Path:
        """
        Returns the path to the top directory of the clone.
        """
        if self.__top_dir_clone is None:
            self.__top_dir_clone = self.__config_path.parent

        return self.__top_dir_clone

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def top_original_path(self) -> Path:
        """
        Returns the path to the top directory of the original.
        """
        if self.__top_dir_original is None:
            config_clone = configparser.ConfigParser()
            config_clone.read(self.__config_path)

            self.__top_dir_original = Path(config_clone['Original']['config']).parent.resolve(True)

        return self.__top_dir_original

    # ------------------------------------------------------------------------------------------------------------------
    def backup_clone_path(self, host: str, backup_no: int) -> Path:
        """
        Returns the path to a host backup of the clone.

        @param host: The name of the host.
        @param backup_no: The backup number.
        """
        return self.top_clone_path.joinpath('pc', host, str(backup_no))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_original_path(self, host: str, backup_no: int) -> Path:
        """
        Returns the path to a host backup of the original.

        @param host: The name of the host.
        @param backup_no: The backup number.
        """
        return self.pc_original_path.joinpath(host, str(backup_no))

    # ------------------------------------------------------------------------------------------------------------------
    def host_dir_clone(self, host: str) -> Path:
        """
        Returns the path to host of the clone.

        @param host: The name of the host.
        """
        return self.top_clone_path.joinpath('pc', host)

    # ------------------------------------------------------------------------------------------------------------------
    def host_dir_original(self, host: str) -> Path:
        """
        Returns the path to host of the original.

        @param host: The name of the host.
        """
        return self.top_original_path.joinpath('pc', host)

# ----------------------------------------------------------------------------------------------------------------------
