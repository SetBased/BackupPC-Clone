"""
BackupPC Clone
"""
import csv
import os
import sqlite3


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
    def __init__(self, database):
        """
        Object constructor.

        :param str database: Path to the SQLite database.
        """
        if DataLayer.instance is not None:
            raise Exception("This class is a singleton!")
        else:
            DataLayer.instance = self

        self.__database = database
        """
        The path to the SQLite database.
        
        :type: str
        """

        self.__connection = sqlite3.connect(database, isolation_level="EXCLUSIVE")
        """
        The connection to the database.

        :type: sqlite3.Connection
        """

        self.__last_rowid = -1
        """
        The last rowid as returns by the last used cursor.

        :type: int
        """

        tmp_dir = os.path.join(os.path.dirname(database), 'tmp')
        self.execute_none('pragma temp_store = 1')
        self.execute_none('pragma temp_store_directory = \'{}\''.format(tmp_dir))

    # ------------------------------------------------------------------------------------------------------------------
    def disconnect(self):
        """
        Disconnects from the SQLite database.
        """
        self.__connection.commit()
        self.__connection.close()

    # ------------------------------------------------------------------------------------------------------------------
    def connect(self):
        """
        Connects to the SQLite database.
        """
        self.__connection = sqlite3.connect(self.__database, isolation_level="EXCLUSIVE")

        tmp_dir = os.path.join(os.path.dirname(self.__database), 'tmp')
        self.execute_none('pragma temp_store = 1')
        self.execute_none('pragma temp_store_directory = \'{}\''.format(tmp_dir))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_delete(self, bck_id):
        """
        Deletes cascading a host backup.

        :param int bck_id: The ID of the host backup.
        """
        self.backup_empty(bck_id)
        self.execute_none('delete from BKC_BACKUP where bck_id=?', (bck_id,))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_empty(self, bck_id):
        """
        Removes the tree from a host backup.

        :param int bck_id: The ID of the host backup.
        """
        self.execute_none('delete from BKC_BACKUP_TREE where bck_id=?', (bck_id,))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_get_all(self):
        """
        Selects all cloned backups.
        """
        sql = """
select hst.hst_name
,      bck.bck_number
from       BKC_HOST   hst
inner join BKC_BACKUP bck  on  bck.hst_id = hst.hst_id"""

        return self.execute_rows(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def backup_get_next(self, end_time):
        """
        Selects the next backup to clone.

        :rtype: dict|None
        """
        sql = """
select bob.bob_host
,      bob.bob_number
,      bob.bob_end_time
,      bob.bob_level
,      bob.bob_type
from            BKC_ORIGINAL_BACKUP bob
left outer join BKC_HOST            hst  on  hst.hst_name = bob.bob_host
left outer join BKC_BACKUP          bck  on  bck.hst_id     = hst.hst_id and
                                             bck.bck_number = bob.bob_number
where bck.bck_id is null 
and   bob.bob_version like '3.%'
and   bob.bob_type in ('full', 'incr')
and   bob.bob_end_time is not null
and  (bob.bob_end_time < ? or ? = -1)
order by bob.bob_type 
,        bob.bob_end_time desc
limit 0, 1"""

        return self.execute_row0(sql, (end_time, end_time))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_get_obsolete(self):
        """
        Selects obsolete host backups.

        :rtype: list[dict]
        """
        sql = """
select hst.hst_name
,      bck.bck_number
from            BKC_HOST            hst
inner join      BKC_BACKUP          bck  on  bck.hst_id = hst.hst_id
left outer join BKC_ORIGINAL_BACKUP bob  on  bob.bob_host   = hst.hst_name and
                                             bob.bob_number = bck.bck_number
where bob.rowid is null
order by hst.hst_name
,        bck.bck_number"""

        return self.execute_rows(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def backup_partially_cloned(self):
        """
        Selects partially cloned host backups.

        :rtype: list[dict]
        """
        sql = """
select hst.hst_name
,      bck.bck_number
from            BKC_HOST   hst
inner join      BKC_BACKUP bck  on  bck.hst_id = hst.hst_id
where ifnull(bck.bck_in_progress, 1) = 1
order by hst.hst_name
,        bck.bck_number"""

        return self.execute_rows(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def backup_set_in_progress(self, bck_id, bck_in_progress):
        """
        Updates the in progress flag of a host backup.

        :param int bck_id: The ID of the host backup.
        :param int bck_in_progress: The in progress flag.
        """
        if bck_in_progress != 0:
            bck_in_progress = 1

        sql = """
update BKC_BACKUP
set    bck_in_progress = ? 
where  bck_id = ?"""

        return self.execute_none(sql, (bck_in_progress, bck_id))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_get_stats(self, bck_id):
        """
        Selects the statistics of a host backup.

        :param int bck_id: The ID of the host backup.
        """
        self.__connection.row_factory = DataLayer.dict_factory

        sql = """
select count(bbt_inode_original)                                   '#files'
,      sum(case when bbt_inode_original is null then 1 else 0 end) '#dirs'
from BKC_BACKUP_TREE
where bck_id = ?"""

        return self.execute_row1(sql, (bck_id,))

    # ------------------------------------------------------------------------------------------------------------------
    def backup_prepare_required_clone_pool_files(self, bck_id):
        """
        Prepares the files required for a host backup that are not yet copied from the original pool to the clone pool.

        :param int bck_id: The ID of the host backup.

        :rtype: int
        """
        self.execute_none('delete from TMP_CLONE_POOL_REQUIRED')

        sql = """
insert into TMP_CLONE_POOL_REQUIRED( bpl_inode_original
,                                    bpl_dir
,                                    bpl_name )
select distinct bpl_inode_original
,               bpl_dir
,               bpl_name
from       BKC_BACKUP_TREE bbt
inner join BKC_POOL        bpl  on bpl.bpl_inode_original = bbt.bbt_inode_original
where bbt.bck_id = ?
and   bpl.bpl_inode_clone is null"""

        self.execute_none(sql, (bck_id,))

        sql = """
select count(distinct bpl_inode_original)
from   TMP_CLONE_POOL_REQUIRED"""

        return self.execute_singleton1(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def backup_prepare_tree(self, bck_id):
        """
        Selects the file entries of a host backup.

        :param int bck_id: The ID of the host backup.

        :rtype: int
        """
        self.execute_none('delete from TMP_BACKUP_TREE')

        sql = """
insert into TMP_BACKUP_TREE( bpl_inode_original
,                            bpl_dir
,                            bpl_name   

,                            bbt_seq                             
,                            bbt_inode_original
,                            bbt_dir
,                            bbt_name )
select bpl.bpl_inode_original
,      bpl.bpl_dir
,      bpl.bpl_name

,      bbt.bbt_seq
,      bbt.bbt_inode_original
,      bbt.bbt_dir
,      bbt.bbt_name
from            BKC_BACKUP_TREE bbt
left outer join BKC_POOL        bpl  on bpl.bpl_inode_original = bbt.bbt_inode_original
where bbt.bck_id = ?"""

        self.execute_none(sql, (bck_id,))

        sql = """
select count(*)
from   TMP_BACKUP_TREE"""

        return self.execute_singleton1(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def backup_yield_required_clone_pool_files(self):
        """
        Selects the pool files required for a host backup that are not yet copied from the original pool to the clone
        pool.
        """
        self.__connection.row_factory = DataLayer.dict_factory

        sql = """
select bpl_inode_original
,      bpl_dir
,      bpl_name
from   TMP_CLONE_POOL_REQUIRED
order by bpl_dir
,        bpl_name"""

        cursor = self.__connection.cursor()
        cursor.execute(sql)
        while True:
            rows = cursor.fetchmany(10000)
            if not rows:
                cursor.close()
                raise StopIteration()
            yield rows

    # ------------------------------------------------------------------------------------------------------------------
    def backup_yield_tree(self):
        """
        Selects the file entries of a host backup.
        """
        self.__connection.row_factory = DataLayer.dict_factory

        sql = """
select bpl_inode_original
,      bpl_dir
,      bpl_name

,      bbt_inode_original
,      bbt_dir
,      bbt_name
from   TMP_BACKUP_TREE
order by bbt_seq
,        bpl_dir
,        bpl_name"""

        cursor = self.__connection.cursor()
        cursor.execute(sql)
        while True:
            rows = cursor.fetchmany(10000)
            if not rows:
                cursor.close()
                raise StopIteration()
            yield rows

    # ------------------------------------------------------------------------------------------------------------------
    def commit(self):
        """
        Commits the current transaction.
        """
        self.__connection.commit()

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def dict_factory(cursor, old_row):
        """
        Dictionary factory for return results with dictionaries.

        :param sqlite3.Cursor cursor: The cursor.
        :param list old_row: A row from the result a a query.

        :rtype: dict
        """
        new_row = {}
        for index, col in enumerate(cursor.description):
            new_row[col[0]] = old_row[index]

        return new_row

    # ------------------------------------------------------------------------------------------------------------------
    def execute_none(self, sql, *params):
        """
        Executes a SQL statement that does not select any rows

        :param str sql: The SQL calling the stored procedure.
        :param iterable params: The arguments for the stored procedure.
        """
        self.__connection.row_factory = None

        cursor = self.__connection.cursor()
        cursor.execute(sql, *params)
        self.__last_rowid = cursor.lastrowid
        cursor.close()

    # ------------------------------------------------------------------------------------------------------------------
    def execute_row0(self, sql, *params):
        """
        Executes a SQL statement that selects 0 or 1 row.

        :param str sql: The SQL calling the stored procedure.
        :param iterable params: The arguments for the stored procedure.

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
    def execute_row1(self, sql, *params):
        """
        Executes a SQL statement that selects 1 row.

        :param str sql: The SQL calling the stored procedure.
        :param iterable params: The arguments for the stored procedure.

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
    def execute_rows(self, sql, *params):
        """
        Executes a SQL statement that selects 0, 1, or more rows.

        :param str sql: The SQL calling the stored procedure.
        :param iterable params: The arguments for the stored procedure.

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
    def execute_singleton0(self, sql, *params):
        """
        Executes a SQL statement that selects 0 or 1 row with 1 column. Returns the value of selected column or None.

        :param str sql: The SQL calling the stored procedure.
        :param iterable params: The arguments for the stored procedure.

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
    def execute_singleton1(self, sql, *params):
        """
        Executes a SQL statement that selects 1 row with 1 column. Returns the value of selected column.

        :param str sql: The SQL calling the stored procedure.
        :param iterable params: The arguments for the stored procedure.

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
    def get_host_id(self, hostname):
        """
        Returns the ID of a host. If the host does not exists it will be inserted.

        :param str hostname: The name of the host.

        :rtype: int
        """
        hst_id = self.execute_singleton0('select hst_id from BKC_HOST where hst_name = ?', (hostname,))
        if hst_id is None:
            self.execute_none('insert into BKC_HOST(hst_name) values(?)', (hostname,))
            hst_id = self.__last_rowid

        return hst_id

    # ------------------------------------------------------------------------------------------------------------------
    def get_bck_id(self, hst_id, bck_number):
        """
        Returns the ID of a host backup. If the backup does not exists it will be inserted.

        :param int hst_id: The ID of the host.
        :param int bck_number: The number of the backup.

        :rtype: int
        """
        sql = """
select bck_id 
from   BKC_BACKUP 
where  hst_id     = ?
and    bck_number = ?"""

        bck_id = self.execute_singleton0(sql, (hst_id, bck_number))
        if bck_id is None:
            self.execute_none('insert into BKC_BACKUP(hst_id, bck_number) values(?, ?)', (hst_id, bck_number))
            bck_id = self.__last_rowid

        return bck_id

    # ------------------------------------------------------------------------------------------------------------------
    def host_delete(self, host):
        """
        Deletes cascading a host.

        :param str host: The name of the host.
        """
        sql = """
select bck_id
from       BKC_HOST   hst
inner join BKC_BACKUP bck  on  bck.hst_id = hst.hst_id
where hst.hst_name = ?"""

        rows = self.execute_rows(sql, (host,))
        for row in rows:
            self.backup_delete(row['bck_id'])

        self.execute_none('delete from BKC_HOST where hst_name=?', (host,))

    # ------------------------------------------------------------------------------------------------------------------
    def host_get_obsolete(self):
        """
        Selects host that are cloned but not longer in original.

        :rtype: list[dict]
        """
        sql = """
select hst.hst_name
from            BKC_HOST            hst
left outer join BKC_ORIGINAL_BACKUP bob  on  bob.bob_host = hst.hst_name
where bob.rowid is null 
order by hst.hst_name"""

        return self.execute_rows(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def import_csv(self, table_name, column_names, path, truncate=True, defaults=None):
        """
        Import a CSV file into a table.

        :param str table_name: The name of the table.
        :param list column_names: The columns names.
        :param str path: The path to the CSV file.
        :param bool truncate:" If True the table will be truncated first.
        :param dict[str,*]|None defaults: The default values for columns not in the CSV file.
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
        with open(path, 'rt') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                # Replace empty string with None.
                for index, field in enumerate(row):
                    if field == '':
                        row[index] = None

                if defaults:
                    row.extend(default_values)
                cursor.execute(sql, row)
        cursor.close()

    # ------------------------------------------------------------------------------------------------------------------
    def original_backup_insert(self, bob_host, bob_number, bob_end_time, bob_version, bob_level, bob_type):
        """
        Inserts an original host backup.
        """
        sql = """
insert into BKC_ORIGINAL_BACKUP( bob_host
,                                bob_number
,                                bob_end_time
,                                bob_version
,                                bob_level
,                                bob_type )
values( ?
,       ?
,       ?
,       ?
,       ?
,       ? )"""
        self.execute_none(sql, (bob_host, bob_number, bob_end_time, bob_version, bob_level, bob_type))

    # ------------------------------------------------------------------------------------------------------------------
    def original_backup_get_stats(self):
        """
        Select statistics of the original backups.

        :rtype: dict
        """
        sql = """
select count(distinct bob_host) '#hosts'
,      count(*)                 '#backups'
from   BKC_ORIGINAL_BACKUP"""

        return self.execute_row1(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def original_backup_truncate(self):
        """
        Truncates table BKC_ORIGINAL_BACKUP.
        """
        self.execute_none('delete from BKC_ORIGINAL_BACKUP')

    # ------------------------------------------------------------------------------------------------------------------
    def overview_get_stats(self):
        """
        Select statistics of the original backups and cloned backups.

        :rtype: dict
        """
        sql = """
select sum(case when cnt1=1 then 1 else 0 end)            n_backups
,      sum(case when cnt1=1 and cnt2=1 then 1 else 0 end) n_cloned_backups
,      sum(case when cnt1=1 and cnt2=0 then 1 else 0 end) n_not_cloned_backups
,      sum(case when cnt1=0 and cnt2=1 then 1 else 0 end) n_obsolete_cloned_backups
from
(
  select sum(case when src=1 then 1 else 0 end) cnt1
  ,      sum(case when src=2 then 1 else 0 end) cnt2
  from (
         select bob_host
         ,      bob_number
         ,      1 src
         from BKC_ORIGINAL_BACKUP

         union all

         select hst.hst_name
         ,      bck.bck_number
         ,      2  src
         from BKC_BACKUP    bck
         join BKC_HOST hst on hst.hst_id = bck.hst_id
       ) t
  group by bob_host
  ,        bob_number
)"""

        return self.execute_row1(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def parameter_get_value(self, prm_code):
        """
        Select the value of a parameter.

        :param str prm_code: The code of the parameter.

        :rtype: *
        """
        return self.execute_singleton1('select prm_value from BKC_PARAMETER where prm_code = ?', (prm_code,))

    # ------------------------------------------------------------------------------------------------------------------
    def parameter_update_value(self, prm_code, prm_value):
        """
        Sets the value of a parameter.

        :param str prm_code: The code of the parameter.
        :param str prm_value: The value of the parameter.
        """
        return self.execute_none('update BKC_PARAMETER set prm_value = ? where prm_code = ?', (prm_value, prm_code))

    # ------------------------------------------------------------------------------------------------------------------
    def pool_delete_obsolete_original_rows(self):
        """
        Deletes rows (i.e. files) from BKC_POOL that are not longer in the actual original pool.
        """
        self.execute_none('delete from TMP_ID')

        sql = """
insert into TMP_ID(tmp_id)
select bpl.bpl_id
from            BKC_POOL bpl
left outer join IMP_POOL imp  on  imp.imp_inode = bpl.bpl_inode_original and
                                  imp.imp_dir   = bpl.bpl_dir            and
                                  imp.imp_name  = bpl.bpl_name
where bpl.bpl_inode_original is not null 
and   imp.rowid is null"""
        self.execute_none(sql)

        sql = """
delete from BKC_POOL
where bpl_id in (select tmp_id from TMP_ID)"""
        self.execute_none(sql)

        return self.execute_singleton1('select count(*) from TMP_ID')

    # ------------------------------------------------------------------------------------------------------------------
    def pool_delete_row(self, bpl_id):
        """
        Deletes a row from the pool metadata.

        :param int bpl_id: The rowid.
        """
        self.execute_none('delete from BKC_POOL where bpl_id=?', (bpl_id,))

    # ------------------------------------------------------------------------------------------------------------------
    def pool_insert_new_original(self):
        """
        Inserts new row into BKC_POOL based on an import from the original pool.
        """
        self.execute_none('delete from TMP_POOL')

        sql = """
insert into TMP_POOL( tmp_inode
,                     tmp_dir
,                     tmp_name )
select tmp_inode
,      tmp_dir
,      tmp_name
from
(
  select bpl_inode_original tmp_inode
  ,      bpl_dir            tmp_dir
  ,      bpl_name           tmp_name
  ,      1                  src
  from   BKC_POOL

  union all

  select imp_inode
  ,      imp_dir
  ,      imp_name
  ,      2                  src
  from   IMP_POOL
) t
group by tmp_inode
,        tmp_dir
,        tmp_name
having sum(case when src=1 then 1 else 0 end) < sum(case when src=2 then 1 else 0 end)"""
        self.execute_none(sql)

        sql = """
insert into BKC_POOL( bpl_inode_original
,                     bpl_dir
,                     bpl_name )
select tmp_inode
,      tmp_dir
,      tmp_name
from   TMP_POOL"""

        self.execute_none(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def pool_prepare_obsolete_clone_files(self):
        """
        Prepares the clone pool files that are obsolete (i.e. not longer in the original pool).

        :rtype: int
        """
        self.execute_none('delete from TMP_CLONE_POOL_OBSOLETE')

        sql = """
insert into TMP_CLONE_POOL_OBSOLETE( bpl_id
,                                    bpl_dir
,                                    bpl_name )
select bpl.bpl_id
,      bpl.bpl_dir
,      bpl.bpl_name
from            BKC_POOL bpl
left outer join IMP_POOL imp  on  imp.imp_inode = bpl.bpl_inode_original and
                                  imp.imp_dir   = bpl.bpl_dir            and
                                  imp.imp_name  = bpl.bpl_name
where  bpl.bpl_inode_clone is not null
and    imp.rowid is null"""

        self.execute_none(sql)

        sql = """
select count(*)
from   TMP_CLONE_POOL_OBSOLETE"""

        return self.execute_singleton1(sql)

    # ------------------------------------------------------------------------------------------------------------------
    def pool_update_by_inode_original(self, bpl_inode_original, bpl_inode_clone, pbl_size, pbl_mtime):
        """
        Sets the inode number of the clone, mtime and size of a file in the pool given a inode number of a file the the
        original pool.

        :param int bpl_inode_original: The inode number of a file file in the original pool.
        :param int bpl_inode_clone: The inode number of the pool file in the clone.
        :param int pbl_size: The size of the pool file.
        :param int pbl_mtime: The mtime of the pool file.
        """
        sql = """
update BKC_POOL
set  bpl_inode_clone = ?
,    bpl_size        = ?
,    bpl_mtime       = ?
where bpl_inode_original = ?"""

        self.execute_none(sql, (bpl_inode_clone, pbl_size, pbl_mtime, bpl_inode_original))

    # ------------------------------------------------------------------------------------------------------------------
    def pool_yield_obsolete_clone_files(self):
        """
        Selects the clone pool files that are obsolete (i.e. not longer in the original pool).
        """
        self.__connection.row_factory = DataLayer.dict_factory

        sql = """
select bpl_id
,      bpl_dir
,      bpl_name
from   TMP_CLONE_POOL_OBSOLETE"""

        cursor = self.__connection.cursor()
        cursor.execute(sql)
        while True:
            rows = cursor.fetchmany(10000)
            if not rows:
                cursor.close()
                raise StopIteration()
            yield rows

    # ------------------------------------------------------------------------------------------------------------------
    def vacuum(self):
        """
        Executes the vacuum command.
        """
        self.execute_none('vacuum')

# ----------------------------------------------------------------------------------------------------------------------
