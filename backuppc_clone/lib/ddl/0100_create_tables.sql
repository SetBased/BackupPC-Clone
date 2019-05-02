/*================================================================================*/
/* DDL SCRIPT                                                                     */
/*================================================================================*/
/*  Title    : BackupPC Clone                                                     */
/*  FileName : backuppc-clone.ecm                                                 */
/*  Platform : SQLite 3                                                           */
/*  Version  :                                                                    */
/*  Date     : donderdag 2 mei 2019                                               */
/*================================================================================*/
/*================================================================================*/
/* CREATE TABLES                                                                  */
/*================================================================================*/

CREATE TABLE BKC_HOST (
  hst_id INTEGER NOT NULL,
  hst_name TEXT NOT NULL,
  PRIMARY KEY (hst_id)
);

CREATE TABLE BKC_BACKUP (
  bck_id INTEGER NOT NULL,
  hst_id INTEGER NOT NULL,
  bck_number INTEGER NOT NULL,
  bck_in_progress INTEGER DEFAULT NULL,
  PRIMARY KEY (bck_id)
);

/*
COMMENT ON COLUMN BKC_BACKUP.bck_in_progress
1 if cloning is in progress, 0 if cloning has finished.
*/

CREATE TABLE BKC_BACKUP_TREE (
  bbt_id INTEGER NOT NULL,
  bck_id INTEGER NOT NULL,
  bbt_seq INTEGER NOT NULL,
  bbt_inode_original INTEGER,
  bbt_dir TEXT,
  bbt_name TEXT,
  PRIMARY KEY (bbt_id)
);

/*
COMMENT ON COLUMN BKC_BACKUP_TREE.bbt_inode_original
The inode number in the original pool
*/

CREATE TABLE BKC_ORIGINAL_BACKUP (
  bob_host TEXT NOT NULL,
  bob_number INTEGER NOT NULL,
  bob_end_time INTEGER,
  bob_version TEXT,
  bob_level INTEGER,
  bob_type TEXT
);

CREATE TABLE BKC_PARAMETER (
  prm_code TEXT NOT NULL,
  prm_description TEXT NOT NULL,
  prm_value TEXT
);

CREATE TABLE BKC_POOL (
  bpl_id INTEGER NOT NULL,
  bpl_inode_original INTEGER,
  bpl_inode_clone INTEGER,
  bpl_dir TEXT NOT NULL,
  bpl_name TEXT NOT NULL,
  bpl_size INTEGER,
  bpl_mtime INTEGER,
  PRIMARY KEY (bpl_id)
);

CREATE TABLE IMP_POOL (
  imp_inode INTEGER NOT NULL,
  imp_dir TEXT NOT NULL,
  imp_name TEXT NOT NULL,
  PRIMARY KEY (imp_inode)
);

CREATE TABLE TMP_BACKUP_TREE (
  bpl_inode_original INTEGER,
  bpl_dir TEXT,
  bpl_name TEXT,
  bbt_seq INTEGER,
  bbt_inode_original INTEGER,
  bbt_dir TEXT,
  bbt_name TEXT
);

CREATE TABLE TMP_CLONE_POOL_OBSOLETE (
  bpl_id INTEGER NOT NULL,
  bpl_dir TEXT NOT NULL,
  bpl_name TEXT NOT NULL
);

CREATE TABLE TMP_CLONE_POOL_REQUIRED (
  bpl_inode_original INTEGER,
  bpl_dir TEXT,
  bpl_name TEXT
);

CREATE TABLE TMP_ID (
  tmp_id INTEGER NOT NULL,
  PRIMARY KEY (tmp_id)
);

CREATE TABLE TMP_POOL (
  tmp_inode INTEGER NOT NULL,
  tmp_dir TEXT NOT NULL,
  tmp_name TEXT NOT NULL,
  PRIMARY KEY (tmp_inode)
);

/*================================================================================*/
/* CREATE INDEXES                                                                 */
/*================================================================================*/

CREATE INDEX IX_BKC_HOST1 ON BKC_HOST (hst_name);

CREATE UNIQUE INDEX IX_BKC_BACKUP1 ON BKC_BACKUP (hst_id, bck_number);

CREATE INDEX IX_BKC_BACKUP2 ON BKC_BACKUP (bck_number);

CREATE INDEX IX_BKC_BACKUP_TREE1 ON BKC_BACKUP_TREE (bck_id);

CREATE INDEX IX_BKC_BACKUP_TREE2 ON BKC_BACKUP_TREE (bbt_inode_original);

CREATE UNIQUE INDEX IX_BKC_ORIGINAL_BACKUP1 ON BKC_ORIGINAL_BACKUP (bob_host, bob_number);

CREATE UNIQUE INDEX IX_BKC_PARAMETER1 ON BKC_PARAMETER (prm_code);

CREATE UNIQUE INDEX IX_BKC_POOL1 ON BKC_POOL (bpl_inode_clone);

CREATE UNIQUE INDEX IX_BKC_POOL2 ON BKC_POOL (bpl_inode_original);

/*================================================================================*/
/* CREATE FOREIGN KEYS                                                            */
/*================================================================================*/

/*ALTER TABLE BKC_BACKUP CREATE FOREIGNKEY FK_BKC_BACKUP_BKC_HOST - Unsupported*/


/*ALTER TABLE BKC_BACKUP_TREE CREATE FOREIGNKEY FK_BKC_BACKUP_TREE_BKC_BACKUP - Unsupported*/

