incremental
===

[![Build Status](https://secure.travis-ci.org/spoofedpacket/incremental.png)](http://travis-ci.org/spoofedpacket/incremental)

## Description

Carries out incremental backups of one folder to another, using
rsync and hardlinks. Archives and expires old backups. 

## Requirements

* Python (ٍ>= 2.7)
* Python modules: argparse, PyYAML
* System: rsync (> 2.6.4)

## Usage
   
Take a look at the supplied incremental.def.yaml, copy it to
/usr/local/etc/incremental.yaml and edit as necessary. You can
also specify an alternate location for the config file:

    ./incremental.py -c /etc/incremental.yaml

To do a dry run, show what would be backed up:

    ./incremental.py -t

To archive and expire old backups:

    ./expire.py

To show what would be archived and expired:

    ./expire.py -t

### Invoke from cron
 
	5 0 * * * root /usr/local/bin/incremental.py > /var/log/incremental.log && /usr/local/bin/expire.py >> /var/log/incremental.log

## Backup folder structure

Each backup is given it's own folder under backup_root:

    /var/tmp/incremental-store/test
    ├── archive
    │   ├── monthly
    │   │   └── 20150601
    │   │       ├── backup.done
    │   │       └── tree
    │   └── weekly
    │       └── 20150607
    │           ├── backup.done
    │           └── tree
    └── backups
        ├── 20150601
        │   ├── backup.done
        │   └── tree
        │       └── 1
        ├── 20150602
        │   ├── backup.done
        │   └── tree
        │       └── 1
        └── latest -> /var/tmp/incremental-store/test/backups/20150602

backup.done contains the timestamp of the last successful backup, which is 
used by expire.py. That data that was backed up is stored under tree/
	
## Archiving and expiring

expire.py archives and expires old backups. It should be run after
incremental.py runs. Backups taken on Sunday are archived to the 
weekly backups folder, backups taken on the first of the month
are archived to the monthly backups folder.

By default, backups are expired after 30 days. Weekly backups expire
after 90 days and monthly backups after 365 days. These options can
be set in the configuration file. Set the expiration time to 0 to keep
the backup forever.

