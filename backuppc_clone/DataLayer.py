import csv
import os
import sqlite3
from pathlib import Path
from typing import Dict, List


class DataLayer:
    """
    Provides an interface to the SQLite3 data_layer
    """
    instance = None
    """
    The singleton instance of this class.

    :type instance: backuppc_clone.DataLayer.DataLayer
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, database: str):
        """
        Object constructor.

        @param str database: Path to the SQLite database.
        """
        if DataLayer.instance is not None:
            raise Exception("This class is a singleton!")
        else:
            DataLayer.instance = self

        self.__database: str = database
        """
        The path to the SQLite database.
        """

        self.__connection: sqlite3.Connection = sqlite3.connect(':memory:')
        """
        The connection to the database.
        """

        self.__last_rowid: int = -1
        """
        The last rowid as returns by the last used cursor.
        """

        self.connect()

    # ------------------------------------------------------------------------------------------------------------------
    def disconnect(self) -> None:
        """
        Disconnects from the SQLite database.
        """
        self.__connection.commit()
        self.__connection.close()

    # ------------------------------------------------------------------------------------------------------------------
    def connect(self) -> None:
        """
        Connects to the SQLite database.
        """
        self.__connection = sqlite3.connect(self.__database, isolation_level="EXCLUSIVE")

        tmp_dir = os.path.join(os.path.dirname(self.__database), 'tmp')
        self.execute_none('pragma temp_store = 1')
        self.execute_none('pragma temp_store_directory = \'{}\''.format(tmp_dir))
        self.execute_none('pragma main.cache_size = -200000')

    # ------------------------------------------------------------------------------------------------------------------
    def backup_delete(self, bck_id: int) -> None:
        """
        Deletes cascading a host backup.

        @param int bck_id: The ID of the host backup.
        """
        self.backup_empty(bck_id)
        self.execute_none('delete from BKC_BACKUP where BCK_ID=?', (bck_id,))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_empty(self, bck_id: int) -> None:
        """
        Removes the tree from a host backup.

        @param int bck_id: The ID of the host backup.
        """
        self.execute_none('delete from BKC_BACKUP_TREE where BCK_ID=?', (bck_id,))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_get_all(self) -> List[Dict]:
        """
        Selects all cloned backups.
        """
        sql = """
              select HST.HST_NAME
                   , BCK.BCK_NUMBER
              from BKC_HOST              HST
                   inner join BKC_BACKUP BCK on BCK.HST_ID = HST.HST_ID"""

        return self.execute_rows(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def backup_get_next(self, end_time: int) -> Dict:
        """
        Selects the next backup to clone.

        :rtype: dict|None
        """
        sql = """
              select BOB.BOB_HOST
                   , BOB.BOB_NUMBER
                   , BOB.BOB_END_TIME
                   , BOB.BOB_LEVEL
                   , BOB.BOB_TYPE
              from BKC_ORIGINAL_BACKUP        BOB
                   left outer join BKC_HOST   HST on HST.HST_NAME = BOB.BOB_HOST
                   left outer join BKC_BACKUP BCK on BCK.HST_ID = HST.HST_ID and
                                                     BCK.BCK_NUMBER = BOB.BOB_NUMBER
              where BCK.BCK_ID is null
                and BOB.BOB_TYPE in ('full', 'incr')
                and BOB.BOB_END_TIME is not null
                and (BOB.BOB_END_TIME < ? or ? = -1)
              order by BOB.BOB_TYPE
                     , BOB.BOB_END_TIME desc
              limit 0, 1"""

        return self.execute_row0(sql, (end_time, end_time))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_get_obsolete(self) -> List[Dict]:
        """
        Selects obsolete host backups.

        :rtype: list[dict]
        """
        sql = """
              select HST.HST_NAME
                   , BCK.BCK_NUMBER
              from BKC_HOST                            HST
                   inner join      BKC_BACKUP          BCK on BCK.HST_ID = HST.HST_ID
                   left outer join BKC_ORIGINAL_BACKUP BOB on BOB.BOB_HOST = HST.HST_NAME and
                                                              BOB.BOB_NUMBER = BCK.BCK_NUMBER
              where BOB.ROWID is null
              order by HST.HST_NAME
                     , BCK.BCK_NUMBER"""

        return self.execute_rows(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def backup_partially_cloned(self) -> List[Dict]:
        """
        Selects partially cloned host backups.

        :rtype: list[dict]
        """
        sql = """
              select HST.HST_NAME
                   , BCK.BCK_NUMBER
              from BKC_HOST              HST
                   inner join BKC_BACKUP BCK on BCK.HST_ID = HST.HST_ID
              where ifnull(BCK.BCK_IN_PROGRESS, 1) = 1
              order by HST.HST_NAME
                     , BCK.BCK_NUMBER"""

        return self.execute_rows(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def backup_set_in_progress(self, bck_id: int, bck_in_progress: int) -> None:
        """
        Updates the in progress flag of a host backup.

        @param int bck_id: The ID of the host backup.
        @param int bck_in_progress: The in progress flag.
        """
        if bck_in_progress != 0:
            bck_in_progress = 1

        sql = """
              update BKC_BACKUP
              set BCK_IN_PROGRESS = ?
              where BCK_ID = ?"""

        self.execute_none(sql, (bck_in_progress, bck_id))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_get_stats(self, bck_id: int) -> Dict:
        """
        Selects the statistics of a host backup.

        @param int bck_id: The ID of the host backup.
        """
        self.__connection.row_factory = DataLayer.dict_factory

        sql = """
              select count(BBT_INODE_ORIGINAL)                                   as '#files'
                   , sum(case when BBT_INODE_ORIGINAL is null then 1 else 0 end) as '#dirs'
              from BKC_BACKUP_TREE
              where BCK_ID = ?"""

        return self.execute_row1(sql, (bck_id,))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_prepare_required_clone_pool_files(self, bck_id: int) -> int:
        """
        Prepares the files required for a host backup that are not yet copied from the original pool to the clone pool.

        @param int bck_id: The ID of the host backup.

        :rtype: int
        """
        self.execute_none('delete from TMP_CLONE_POOL_REQUIRED')

        sql = """
              insert into TMP_CLONE_POOL_REQUIRED( BPL_INODE_ORIGINAL
                                                 , BPL_DIR
                                                 , BPL_NAME)
              select distinct BPL_INODE_ORIGINAL
                            , BPL_DIR
                            , BPL_NAME
              from BKC_BACKUP_TREE     BBT
                   inner join BKC_POOL BPL on BPL.BPL_INODE_ORIGINAL = BBT.BBT_INODE_ORIGINAL
              where BBT.BCK_ID = ?
                and BPL.BPL_INODE_CLONE is null"""

        self.execute_none(sql, (bck_id,))

        sql = """
              select count(distinct BPL_INODE_ORIGINAL)
              from TMP_CLONE_POOL_REQUIRED"""

        return self.execute_singleton1(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def backup_prepare_tree(self, bck_id: int) -> int:
        """
        Selects the file entries of a host backup.

        @param int bck_id: The ID of the host backup.

        :rtype: int
        """
        self.execute_none('delete from TMP_BACKUP_TREE')

        sql = """
              insert into TMP_BACKUP_TREE( BPL_INODE_ORIGINAL
                                         , BPL_DIR
                                         , BPL_NAME
                                         , BBT_SEQ
                                         , BBT_INODE_ORIGINAL
                                         , BBT_DIR
                                         , BBT_NAME)
              select BPL.BPL_INODE_ORIGINAL
                   , BPL.BPL_DIR
                   , BPL.BPL_NAME

                   , BBT.BBT_SEQ
                   , BBT.BBT_INODE_ORIGINAL
                   , BBT.BBT_DIR
                   , BBT.BBT_NAME
              from BKC_BACKUP_TREE          BBT
                   left outer join BKC_POOL BPL on BPL.BPL_INODE_ORIGINAL = BBT.BBT_INODE_ORIGINAL
              where BBT.BCK_ID = ?"""

        self.execute_none(sql, (bck_id,))

        sql = """
              select count(*)
              from TMP_BACKUP_TREE"""

        return self.execute_singleton1(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def backup_yield_required_clone_pool_files(self):
        """
        Selects the pool files required for a host backup that are not yet copied from the original pool to the clone
        pool.
        """
        self.__connection.row_factory = DataLayer.dict_factory

        sql = """
              select BPL_INODE_ORIGINAL
                   , BPL_DIR
                   , BPL_NAME
              from TMP_CLONE_POOL_REQUIRED
              order by BPL_DIR
                     , BPL_NAME"""

        cursor = self.__connection.cursor()
        cursor.execute(sql)
        while True:
            rows = cursor.fetchmany(10000)
            if not rows:
                cursor.close()
                return
            yield rows

    # ------------------------------------------------------------------------------------------------------------------
    def backup_yield_tree(self):
        """
        Selects the file entries of a host backup.
        """
        self.__connection.row_factory = DataLayer.dict_factory

        sql = """
              select BPL_INODE_ORIGINAL
                   , BPL_DIR
                   , BPL_NAME

                   , BBT_INODE_ORIGINAL
                   , BBT_DIR
                   , BBT_NAME
              from TMP_BACKUP_TREE
              order by BBT_SEQ
                     , BPL_DIR
                     , BPL_NAME"""

        cursor = self.__connection.cursor()
        cursor.execute(sql)
        while True:
            rows = cursor.fetchmany(10000)
            if not rows:
                cursor.close()
                return
            yield rows

    # ------------------------------------------------------------------------------------------------------------------
    def commit(self) -> None:
        """
        Commits the current transaction.
        """
        self.__connection.commit()

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def dict_factory(cursor: sqlite3.Cursor, old_row: List) -> Dict:
        """
        Dictionary factory for return results with dictionaries.

        @param Cursor cursor: The cursor.
        @param list old_row: A row from the result a query.

        :rtype: dict
        """
        new_row = {}
        for index, col in enumerate(cursor.description):
            new_row[col[0]] = old_row[index]

        return new_row

    # ------------------------------------------------------------------------------------------------------------------
    def execute_none(self, sql: str, *params) -> int:
        """
        Executes a SQL statement that does not select any rows.

        @param str sql: The SQL calling the stored procedure.
        @param iterable params: The arguments for the stored procedure.
        """
        self.__connection.row_factory = None

        cursor = self.__connection.cursor()
        cursor.execute(sql, *params)
        self.__last_rowid = cursor.lastrowid
        row_count = cursor.rowcount
        cursor.close()

        return row_count

    # ------------------------------------------------------------------------------------------------------------------
    def execute_row0(self, sql: str, *params) -> Dict | None:
        """
        Executes a SQL statement that selects 0 or 1 row.

        @param str sql: The SQL calling the stored procedure.
        @param iterable params: The arguments for the stored procedure.

        :rtype: dict
        """
        self.__connection.row_factory = DataLayer.dict_factory

        cursor = self.__connection.cursor()
        cursor.execute(sql, *params)
        rows = cursor.fetchall()
        self.__last_rowid = cursor.lastrowid
        cursor.close()

        if len(rows) == 0:
            return None

        return rows[0]

    # ------------------------------------------------------------------------------------------------------------------
    def execute_row1(self, sql: str, *params) -> Dict:
        """
        Executes a SQL statement that selects 1 row.

        @param str sql: The SQL calling the stored procedure.
        @param iterable params: The arguments for the stored procedure.

        :rtype: dict
        """
        self.__connection.row_factory = DataLayer.dict_factory

        cursor = self.__connection.cursor()
        cursor.execute(sql, *params)
        rows = cursor.fetchall()
        self.__last_rowid = cursor.lastrowid
        cursor.close()

        return rows[0]

    # ------------------------------------------------------------------------------------------------------------------
    def execute_rows(self, sql: str, *params) -> List[Dict]:
        """
        Executes a SQL statement that selects 0, 1, or more rows.

        @param str sql: The SQL calling the stored procedure.
        @param iterable params: The arguments for the stored procedure.

        :rtype: list[dict]
        """
        self.__connection.row_factory = DataLayer.dict_factory

        cursor = self.__connection.cursor()
        cursor.execute(sql, *params)
        rows = cursor.fetchall()
        self.__last_rowid = cursor.lastrowid
        cursor.close()

        return rows

    # ------------------------------------------------------------------------------------------------------------------
    def execute_singleton0(self, sql: str, *params):
        """
        Executes a SQL statement that selects 0 or 1 row with 1 column. Returns the value of selected column or None.

        @param str sql: The SQL calling the stored procedure.
        @param iterable params: The arguments for the stored procedure.

        :rtype: *
        """
        self.__connection.row_factory = None

        cursor = self.__connection.cursor()
        cursor.execute(sql, *params)
        row = cursor.fetchone()
        if row:
            ret = row[0]
        else:
            ret = None
        self.__last_rowid = cursor.lastrowid
        cursor.close()

        return ret

    # ------------------------------------------------------------------------------------------------------------------
    def execute_singleton1(self, sql: str, *params):
        """
        Executes a SQL statement that selects 1 row with 1 column. Returns the value of the selected column.

        @param str sql: The SQL calling the stored procedure.
        @param iterable params: The arguments for the stored procedure.

        :rtype: *
        """
        self.__connection.row_factory = None

        cursor = self.__connection.cursor()
        cursor.execute(sql, *params)
        ret = cursor.fetchone()[0]
        self.__last_rowid = cursor.lastrowid
        cursor.close()

        return ret

    # ------------------------------------------------------------------------------------------------------------------
    def get_host_id(self, hostname: str) -> int:
        """
        Returns the ID of a host. If the host does not exist, it will be inserted.

        @param str hostname: The name of the host.

        :rtype: int
        """
        hst_id = self.execute_singleton0('select HST_ID from BKC_HOST where HST_NAME = ?', (hostname,))
        if hst_id is None:
            self.execute_none('insert into BKC_HOST(HST_NAME) values(?)', (hostname,))
            hst_id = self.__last_rowid

        return hst_id

    # ------------------------------------------------------------------------------------------------------------------
    def get_bck_id(self, hst_id: int, bck_number: int) -> int:
        """
        Returns the ID of a host backup. If the backup does not exist, it will be inserted.

        @param int hst_id: The ID of the host.
        @param int bck_number: The sequence number of the backup.

        :rtype: int
        """
        sql = """
              select BCK_ID
              from BKC_BACKUP
              where HST_ID = ?
                and BCK_NUMBER = ?"""

        bck_id = self.execute_singleton0(sql, (hst_id, bck_number))
        if bck_id is None:
            self.execute_none('insert into BKC_BACKUP(HST_ID, BCK_NUMBER) values(?, ?)', (hst_id, bck_number))
            bck_id = self.__last_rowid

        return bck_id

    # ------------------------------------------------------------------------------------------------------------------
    def host_delete(self, host: str) -> None:
        """
        Deletes cascading a host.

        @param str host: The name of the host.
        """
        sql = """
              select BCK_ID
              from BKC_HOST              HST
                   inner join BKC_BACKUP BCK on BCK.HST_ID = HST.HST_ID
              where HST.HST_NAME = ?"""

        rows = self.execute_rows(sql, (host,))
        for row in rows:
            self.backup_delete(row['bck_id'])

        self.execute_none('delete from BKC_HOST where HST_NAME=?', (host,))

    # ------------------------------------------------------------------------------------------------------------------
    def host_get_obsolete(self) -> List[Dict]:
        """
        Selects hosts that are cloned but no longer in the original pool.

        :rtype: list[dict]
        """
        sql = """
              select HST.HST_NAME
              from BKC_HOST                            HST
                   left outer join BKC_ORIGINAL_BACKUP BOB on BOB.BOB_HOST = HST.HST_NAME
              where BOB.ROWID is null
              order by HST.HST_NAME"""

        return self.execute_rows(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def import_csv(self,
                   table_name: str,
                   column_names: List[str],
                   path: Path,
                   truncate: bool = True,
                   defaults: Dict = None):
        """
        Import a CSV file into a table.

        @param table_name: The name of the table.
        @param column_names: The column names.
        @param path: The path to the CSV file.
        @param truncate: If True, the table will be truncated first.
        @param defaults: The default values for columns not in the CSV file.
        """
        if truncate:
            self.execute_none('delete from {}'.format(table_name))

        default_values = []
        if defaults:
            for column_name in defaults:
                column_names.append(column_name)
                default_values.append(defaults[column_name])

        place_holders = []
        for _ in range(0, len(column_names)):
            place_holders.append('?')

        sql = 'insert into {}({}) values ({})'.format(table_name, ', '.join(column_names), ', '.join(place_holders))
        cursor = self.__connection.cursor()
        rows = []
        with open(path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                # Replace empty string with None.
                for index, field in enumerate(row):
                    if field == '':
                        row[index] = None

                if defaults:
                    row.extend(default_values)

                rows.append(row)

                if len(rows) == 1000:
                    cursor.executemany(sql, rows)
                    rows = []

        if rows:
            cursor.executemany(sql, rows)

        cursor.close()

    # ------------------------------------------------------------------------------------------------------------------
    def original_backup_insert(self,
                               bob_host: str,
                               bob_number: int,
                               bob_end_time: str,
                               bob_level: int,
                               bob_type: str) -> None:
        """
        Inserts an original host backup.
        """
        sql = """
              insert into BKC_ORIGINAL_BACKUP( bob_host
                                             , bob_number
                                             , bob_end_time
                                             , bob_level
                                             , bob_type)
              values
                  ( ?
                  , ?
                  , ?
                  , ?
                  , ?)"""
        self.execute_none(sql, (bob_host, bob_number, bob_end_time, bob_level, bob_type))

    # ------------------------------------------------------------------------------------------------------------------
    def original_backup_get_stats(self) -> Dict:
        """
        Select statistics of the original backups.

        :rtype: dict
        """
        sql = """
              select count(distinct BOB_HOST) as '#hosts'
                   , count(*)                 as '#backups'
              from BKC_ORIGINAL_BACKUP"""

        return self.execute_row1(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def original_backup_truncate(self) -> None:
        """
        Truncates table BKC_ORIGINAL_BACKUP.
        """
        self.execute_none('delete from BKC_ORIGINAL_BACKUP')

    # ------------------------------------------------------------------------------------------------------------------
    def overview_get_stats(self) -> Dict:
        """
        Select statistics of the original backups and cloned backups.

        :rtype: dict
        """
        sql = """
              select sum(case when cnt1 = 1 then 1 else 0 end)              as n_backups
                   , sum(case when cnt1 = 1 and cnt2 = 1 then 1 else 0 end) as n_cloned_backups
                   , sum(case when cnt1 = 1 and cnt2 = 0 then 1 else 0 end) as n_not_cloned_backups
                   , sum(case when cnt1 = 0 and cnt2 = 1 then 1 else 0 end) as n_obsolete_cloned_backups
              from ( select sum(case when src = 1 then 1 else 0 end) as cnt1
                          , sum(case when src = 2 then 1 else 0 end) as cnt2
                     from ( select bob_host
                                 , bob_number
                                 , 1 as src
                            from BKC_ORIGINAL_BACKUP

                            union all

                            select hst.hst_name
                                 , bck.bck_number
                                 , 2 as src
                            from BKC_BACKUP    bck
                                 join BKC_HOST hst on hst.hst_id = bck.hst_id ) T
                     group by bob_host
                            , bob_number )"""

        return self.execute_row1(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def parameter_get_value(self, prm_code: str) -> str:
        """
        Select the value of a parameter.

        @param str prm_code: The code of the parameter.

        :rtype: *
        """
        return self.execute_singleton1('select prm_value from BKC_PARAMETER where prm_code = ?', (prm_code,))

    # ------------------------------------------------------------------------------------------------------------------
    def parameter_update_value(self, prm_code: str, prm_value: str) -> None:
        """
        Sets the value of a parameter.

        @param str prm_code: The code of the parameter.
        @param str prm_value: The value of the parameter.
        """
        self.execute_none('update bkc_parameter set prm_value = ? where prm_code = ?', (prm_value, prm_code))

    # ------------------------------------------------------------------------------------------------------------------
    def pool_delete_obsolete_original_rows(self) -> int:
        """
        Deletes rows (i.e., files) from BKC_POOL that are no longer in the actual original pool.
        """
        self.execute_none('delete from TMP_ID')

        sql = """
              insert into TMP_ID(tmp_id)
              select bpl.bpl_id
              from BKC_POOL                 bpl
                   left outer join IMP_POOL imp on imp.imp_inode = bpl.bpl_inode_original and
                                                   imp.imp_dir = bpl.bpl_dir and
                                                   imp.imp_name = bpl.bpl_name
              where bpl.bpl_inode_original is not null
                and imp.rowid is null"""
        self.execute_none(sql)

        sql = """
              delete
              from BKC_POOL
              where bpl_id in ( select tmp_id
                                from TMP_ID )"""
        self.execute_none(sql)

        return self.execute_singleton1('select count(*) from TMP_ID')

    # ------------------------------------------------------------------------------------------------------------------
    def pool_delete_row(self, bpl_id: int) -> None:
        """
        Deletes a row from the pool metadata.

        @param int bpl_id: The rowid.
        """
        self.execute_none('delete from BKC_POOL where bpl_id=?', (bpl_id,))

    # ------------------------------------------------------------------------------------------------------------------
    def pool_insert_new_original(self) -> None:
        """
        Inserts new row into BKC_POOL based on an import from the original pool.
        """
        self.execute_none('delete from TMP_POOL')

        sql = """
              insert into TMP_POOL( tmp_inode
                                  , tmp_dir
                                  , tmp_name)
              select TMP_INODE
                   , TMP_DIR
                   , TMP_NAME
              from ( select bpl_inode_original as tmp_inode
                          , bpl_dir            as tmp_dir
                          , bpl_name           as tmp_name
                          , 1                  as src
                     from BKC_POOL

                     union all

                     select imp_inode
                          , imp_dir
                          , imp_name
                          , 2 as src
                     from IMP_POOL ) T
              group by tmp_inode
                     , tmp_dir
                     , tmp_name
              having sum(case when src = 1 then 1 else 0 end) < sum(case when src = 2 then 1 else 0 end)"""
        self.execute_none(sql)

        sql = """
              insert into BKC_POOL( bpl_inode_original
                                  , bpl_dir
                                  , bpl_name)
              select tmp_inode
                   , tmp_dir
                   , tmp_name
              from TMP_POOL"""

        self.execute_none(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def clone_pool_obsolete_files_prepare(self) -> int:
        """
        Prepares the clone pool files that are obsolete (i.e., no longer in the original pool).
        """
        self.execute_none('delete from TMP_CLONE_POOL_OBSOLETE')

        sql = """
              insert into TMP_CLONE_POOL_OBSOLETE( bpl_id
                                                 , bpl_dir
                                                 , bpl_name)
              select bpl.bpl_id
                   , bpl.bpl_dir
                   , bpl.bpl_name
              from BKC_POOL                 bpl
                   left outer join IMP_POOL imp on imp.imp_inode = bpl.bpl_inode_original and
                                                   imp.imp_dir = bpl.bpl_dir and
                                                   imp.imp_name = bpl.bpl_name
              where BPL.bpl_inode_clone is not null
                and IMP.rowid is null"""

        self.execute_none(sql)

        sql = """
              select count(*)
              from TMP_CLONE_POOL_OBSOLETE"""

        return self.execute_singleton1(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def clone_pool_delete_missing(self) -> int:
        """
        Removes rows from BKC_POOL with files that are not found in the clone pool.
        """
        self.execute_none('delete from TMP_ID')

        sql = """
              insert into TMP_ID(TMP_ID)
              select BPL.BPL_ID
              from BKC_POOL                 BPL
                   left outer join IMP_POOL IMP on IMP.IMP_INODE = BPL.BPL_INODE_CLONE and
                                                   IMP.IMP_DIR = BPL.BPL_DIR and
                                                   IMP.IMP_NAME = BPL.BPL_NAME
              where BPL.BPL_INODE_CLONE is not null
                and IMP.ROWID is null"""

        self.execute_none(sql)

        sql = """
              delete
              from BKC_POOL
              where bpl_id in ( select tmp_id
                                from TMP_ID )"""

        return self.execute_none(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def pool_update_by_inode_original(self,
                                      bpl_inode_original: int,
                                      bpl_inode_clone: int,
                                      pbl_size: int,
                                      pbl_mtime: int) -> None:
        """
        Sets the inode number of the clone, mtime and size of a file in the pool given an inode number of a file the
        original pool.

        @param int bpl_inode_original: The inode number of a file in the original pool.
        @param int bpl_inode_clone: The inode number of the pool file in the clone.
        @param int pbl_size: The size of the pool file.
        @param int pbl_mtime: The mtime of the pool file.
        """
        sql = """
              update BKC_POOL
              set bpl_inode_clone = ?
                , bpl_size        = ?
                , bpl_mtime       = ?
              where BPL_INODE_ORIGINAL = ?"""

        self.execute_none(sql, (bpl_inode_clone, pbl_size, pbl_mtime, bpl_inode_original))

    # ------------------------------------------------------------------------------------------------------------------
    def clone_pool_obsolete_files_yield(self):
        """
        Selects the clone pool files that are obsolete (i.e., no longer in the original pool).
        """
        self.__connection.row_factory = DataLayer.dict_factory

        sql = """
              select bpl_id
                   , bpl_dir
                   , bpl_name
              from TMP_CLONE_POOL_OBSOLETE"""

        cursor = self.__connection.cursor()
        cursor.execute(sql)
        while True:
            rows = cursor.fetchmany(10000)
            if not rows:
                cursor.close()
                return
            yield rows

    # ------------------------------------------------------------------------------------------------------------------
    def vacuum(self) -> None:
        """
        Executes the vacuum command.
        """
        self.execute_none('vacuum')

# ----------------------------------------------------------------------------------------------------------------------
