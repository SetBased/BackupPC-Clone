Miscellaneous
=============

In this chapter we discuss miscellaneous aspects related to or about BackupPC-Clone.

.. _ext4-inodes:

Ext4 Filesystem and Inodes
--------------------------

The ext4 filesystem is still one of the most used filesystems. One of the properties of the ext4 filesystem is that the
number of inodes is fixed and can not be increased later. BackupPC requires relatively a lot of inodes due to fact it is
using many hardlinks to the same file.

When creating an ext4 filesystem for a clone make sure that this filesystem has enough inodes. One can compare the
number of inodes with the following commands:

.. code-block:: sh

  tune2fs -l `df /var/lib/BackupPC       | awk '{if (NR==2) print $1}'` | grep -i 'inode count'
  tune2fs -l `df /var/lib/BackupPC-Clone | awk '{if (NR==2) print $1}'` | grep -i 'inode count'

The ``-i``, ``-I``, and ``-N`` option of ``mke2fs`` impact the number of inodes created.

.. _cryptsetup:

Clone on Removable Media
------------------------

When creating a clone on removable media it is recommended to encrypt the filesystem such that in case of loss or theft
your data is still save.

Suppose your external disk is available under ``/dev/sdh1`` you can encrypt your external disk with the following
commands:

.. code-block:: sh

  cryptsetup --verify-passphrase --cipher aes-cbc-essiv:sha256 --key-size 256 luksFormat /dev/sdh1
  cryptsetup luksOpen /dev/sdh1 sdh1-luks

The encrypted disk will be available at ``/dev/mapper/sdh1-luks``.

We found no noticeable performance impact when using disk encryption

.. _reserved-blocks:

Reserved blocks
---------------

When using a dedicated partition (and an ext4 filesystem) for the clone you might set the percentage of the filesystem
blocks reserved for the super-user to 0 using the ``-m`` option of the ``mke2fs`` command.

Example Creating Filesystem for Clone
-------------------------------------

In this section we give an example how to create a filesystem for a clone of BackupPC.

.. code-block:: sh

  cryptsetup --verify-passphrase --cipher aes-cbc-essiv:sha256 --key-size 256 luksFormat /dev/sdh1
  cryptsetup luksOpen /dev/sdh1 sdh1-luks

  mke2fs -t ext4 -i 16384 -m 0 /dev/mapper/sdh1-luks

  mkdir /var/lib/BackupPC-Clone

  mount -t ext4 /dev/mapper/sdh1-luks /var/lib/BackupPC-Clone

  chown backuppc.backuppc /var/lib/BackupPC-Clone

See :ref:`cryptsetup` for more information about the `cryptsetup` commands, see :ref:`ext4-inodes` and
:ref:`reserved-blocks` for more information on the ``-i`` and ``-m`` options of the ``mke2fs`` command.

Verifying a Clone Backup
------------------------

A backup paramount for your company regardless of its size ans you must not trust BackupPC-Clone blindly.

You can verify BackupPC-Clone has created a correct clone of a host backup simply with the following command (replace
``host`` and ``num`` with the actual hostname and backup number):

.. code-block:: sh

  diff --recursive --brief /var/lib/BackupPC/pc/host/num/ /var/lib/BackupPC-Clone/clone/pc/host/num/

You can ignore the following message:

.. code-block:: text

  Only in /var/lib/BackupPC/pc/host/num/: backuppc-clone.csv
