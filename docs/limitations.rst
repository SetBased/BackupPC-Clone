Limitations
===========

In this chapter we discus the limitations of BackupPC-Clone.

* Currently only BackupPC 3.x is supported by BackupPC-Clone. We plan to support BackupPC 4.x when we have migrated our
  servers to CentOS 8.

* BackupPC-Clone uses the combination of filename and inode number for identifying files in the pool of BackupPC. Hence,
  if between two consecutive scans of the pool of BackupPC by BackupPC-Clone a pool file is deleted and a new file
  (different from the deleted pool file) is added to the pool of BackupPC with the same MD5 hash (i.e. a MD5 collision
  between the deleted and new file) and is associated with the same inode as the deleted file BackupPC-Clone will not
  detect that the file has been changed in the pool of BackupPC. We regard the chance on such an event very unlikely.
