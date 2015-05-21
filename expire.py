#!/usr/bin/python

'''
expire.py:

 Examines the backup directory tree and deletes any backups
 that are expired. Should be run after incremental.py.

'''

__author__ = "Robert Gallagher"
__version__ = "0.2"

# Modules
import os
import time
import shutil
import string
import argparse
import yaml

# Command line arguments
argparser = argparse.ArgumentParser()
argparser.add_argument('-c', action='store', dest='CFG', help='Config file location (defaults to /usr/local/etc/incremental.yaml)')
argparser.add_argument('-t', action='store_true', dest='TEST', help='Run in test mode. Show which directories would be expired.')
arguments  = argparser.parse_args()
CFG = arguments.CFG
TEST = arguments.TEST

# Ensure CFG is set, if the user hasn't supplied it
if CFG == None:
   CFG = "/usr/local/etc/incremental.yaml"

# Get the current time
now = time.time()

# Process config
try:
   with open(CFG, 'r') as ymlfile:
       cfg = yaml.load(ymlfile)
except IOError as e:
       print ("ERROR: Could not read configuration!: {0}".format(err))

# Consult config and obtain list of directories to consider for expiration
backup_root = os.path.join(cfg['backup_root'], '')
backup_locations = cfg['backup_locations']

# Gather expiration settings
try:
   expire_default_days = cfg['expire_default']
except KeyError:
   print ("INFO: expire_default not set, setting it to 30 days.\n")
   expire_default_days = 30
   pass

try:
   expire_weekly_days = cfg['expire_weekly']
except KeyError:
   print ("INFO: expire_weekly not set, setting it to 90 days.\n")
   expire_weekly_days = 90
   pass

try:
   expire_monthly_days = cfg['expire_monthly']
except KeyError:
   print ("INFO: expire_monthly not set, setting it to 365 days.\n")
   expire_monthly_days = 365
   pass

expire_default = 86400*expire_default_days
expire_weekly = 86400*expire_weekly_days
expire_monthly = 86400*expire_monthly_days

# Process each backup directory. If the ctime of the directory is > than the
# configured expiration time (in days), delete the directory tree.
#
for name, path in backup_locations.items():
   expire_root_dir = os.path.join(backup_root, name, '')
   for dir in os.listdir(expire_root_dir):
       full_path = os.path.join(expire_root_dir, dir)
       if os.path.isdir(full_path):
         timestamp = os.path.getctime(full_path)
         if now-expire_default > timestamp:
             try:
                  if TEST:
                    print("TEST: Would remove " + full_path)
                  else:
                    print("Removing " + full_path)
                    shutil.rmtree(full_path)
             except Exception as e:
                  print ("ERROR: Couldn't remove directory!: {0}".format(err))
                  pass
             else: 
                  print("Done.")
