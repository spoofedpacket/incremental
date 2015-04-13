incremental
===

## Description

Carries out incremental backups of one folder to another, using
rsync and hardlinks. Intended to be run daily, after midnight.

## Requirements

* Python (tested with 2.7)
* Python modules: argparse, yaml
* System: rsync (> 2.6.4)

## Usage
   
Take a look at the supplied incremental.def.yaml, copy it to
/usr/local/etc/incremental.yaml and edit as necessary. You can
also specify an alternate location for the config file:

    ./incremental.py -c /etc/incremental.yaml

To do a dry run, show what would be backed up:

    ./incremental.py -t

### Invoke from cron
 
    0 1 * * * root /usr/local/bin/incremental.py > /var/log/incremental.log
