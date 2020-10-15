[![Travis Status](https://travis-ci.org/oldarmyc/accord.svg?branch=master)](https://travis-ci.org/oldarmyc/accord) &nbsp; [![Anaconda-Server Badge](https://anaconda.org/ae5-admin/accord/badges/latest_release_date.svg)](https://anaconda.org/ae5-admin/accord) &nbsp; [![Anaconda-Server Badge](https://anaconda.org/ae5-admin/accord/badges/version.svg)](https://anaconda.org/ae5-admin/accord)

Accord
======

Use this Python package to help facilitate the backup and restore of your Anaconda Enterprise 5 installation.

To backup the system, you'll need to install the ``accord`` package on the master node of the AE cluster.

### Setup conda environment and install accord

Download and install Miniconda3
```sh
# Get miniconda3 and install it
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh  # Accept the license and take the defaults

# Source bashrc to pick up conda paths
source ~/.bashrc
```

Create and activate conda environment
```sh
# Create profile, and install package
conda create -n backup python=3.7 -y
conda activate backup
conda install -c ae5-admin accord -y
```

### Syncing
You have the option to sync the backup files to another Anaconda Enterprise cluster. To do so, the user specified to do the sync must meet the following criteria:
- User must exist on both systems
- User can sudo to root without a password
- User can SSH to the destination system with passwordless sudo

**NOTE:** When performing a backup, connectivity between the two systems will be tested to confirm that passwordless SSH is working before any backup or sync operation is attempted. During that test, the destination directory where the restored files will be placed is also created.

### Backup
The backup process does not interfere with the running system, and therefore can be performed while others are using the platform.

**NOTE:** Any files *in a running project that have not been committed to your version control repository* **will not** be backed up.

Run the following command to perform a backup:

```sh
accord -a backup
```

All files being backed up are placed in the ``/opt/anaconda_backup`` directory by default, which includes the following:

- A dump of the Postgres database
- All Gravity-related files
- All secrets and config files used in the system (stored in ``[BACKUP_DIRECTORY]/secrets``)
- Ingress definitions that defines the domain (stored in ``[BACKUP_DIRECTORY]/ingress``)
- The object store, which includes all project data

You can change the default backup location by passing the ``-d`` or ``--directory`` option to the command, followed by the desired path.

**NOTE:** You must use the same directory for both the backup and restore operations. So, if you specify a different backup directory (e.g., ``/usr/local/backups``), you must use the same directory when performing a restore.

To sync the backup between Anaconda Enterprise clusters, you will want to use the ``-s`` flag to signify that a sync will need to take place after the backup has completed. Along with the ``SYNC_USER`` and ``SYNC_NODE`` flags, the application will move the backup files automatically to the specified node using the specified user provided.

```sh
accord -a backup -s -u <SYNC_USER> -n <SYNC_NODE>
```
You can also add the ``--archive`` flag to the backup command, to create a .tar file of the backup directory. This will create a timestamped ``.tar.gz`` file in the ``[BACKUP_DIRECTORY]`` that includes all the backed up files and secrets.

```sh
accord -a backup --archive
```
You can also choose to backup **only the Anaconda Enterprise repositories that have been mirrored**, to move them from one cluster to another. Instead of mirroring on each installed cluster, you can perform the mirror on one AE5 cluster, then backup and restore the repositories across all AE5 clusters in an environment.

In this case, include the following options with the ``backup`` command:

```sh
accord -a backup --repos-only -u <SYNC USER> -n <SYNC NODE>
```

Where:

* ``--repos-only`` = Backup the repository database only, and sync the repository on the running cluster to another cluster.

* ``-u`` = The username to use for the sync operation described above. The user must have passwordless ssh setup to successfully sync.

* ``-n`` = The IP address or DNS name of the node to sync the repository and database backup to (i.e., the AE5 master node on the target cluster).

### Restore

Run the following command to restore the backup files from the default directory ``/opt/anaconda_backup``, whether on the same cluster or in a DR setup.

```sh
accord -a restore
```

If you specified an alternate directory to store the backup files, specify the location to restore the files from using the ``-d`` or ``--directory`` option, followed by the path to the directory that was specified during the backup operation.

If you chose to backup only the mirrored repositories, pass the ``--repos-only`` option to the restore command:

```sh
accord -a restore --repos-only
```

**NOTE:** During the restore process, the platform configuration file is replaced by the config map that was backed up from the source cluster. To prevent the platform config file from being replaced during the restore, pass the ``--no-config`` option to the command:

```sh
accord -a restore --no-config
```

**NOTE:** During the backup process, a 0 byte file named ``restore`` is placed in the backup directory. This file signals that a backup was completed, but has not yet been restored. The restore process checks for the presence of this file before running the restore operation. When the restore process has completed, it removes that file from the backup directory.

If you want to restore again from the same backup files, and the 0 byte ``restore`` file was removed from the backup directory location after the inital restore process completed, you must pass an ``--override`` flag to run the restore process again:

```sh
accord -a restore --override
```

If you would like to restore the ingress definitions from the backup, pass the ``--ingress`` option to the restore command:

```sh
accord -a restore --ingress
```

You can also restore from a ``.tar.gz`` backup file created by using the ``--archive`` flag, to specify a backup other than the latest backup. If you specified a non-default location when you created the backup, you'll need to specify that same location for the restore.

```sh
accord -a restore --restore-file ae5_backup.tar.gz
```

**CAUTION:**  When you use this method, the archive is extracted into the ``[BACKUP_DIRECTORY]`` and **will overwrite any files in that location**.
