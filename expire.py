#!/usr/bin/python

'''
expire.py:

 Examines the backup directory tree and deletes any backups
 that are expired. Should be run after incremental.py.

'''

__author__ = "Robert Gallagher"
__version__ = "0.1"

# Modules
import os
import time
import shutil
import string
import argparse
import yaml

# Set some times
expired = 86400*15
now = time.time()

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

# Process config
try:
   with open(CFG, 'r') as ymlfile:
       cfg = yaml.load(ymlfile)
except IOError as e:
       print ("I/O error: {0}".format(err))

# Consult config and obtain list of directories to consider for expiration
backup_root = os.path.join(cfg['backup_root'], '')
backup_locations = cfg['backup_locations']

# Process each backup directory. If the mtime of the directory is > than the 
# configured expiration time (in days), delete the directory tree.
for name, path in backup_locations.items():
   expire_root_dir = os.path.join(backup_root, name, '')
   for dir in os.listdir(expire_root_dir):
       full_path = os.path.join(expire_root_dir, dir)
       if os.path.isdir(full_path):
         timestamp = os.path.getmtime(full_path)
         if now-expired > timestamp:
             try:
                  if TEST:
                    print("Would remove " + full_path)
                  else:
                    print("Removing " + full_path)
                    shutil.rmtree(full_path)
             except Exception as e:
                  print ("Couldn't remove directory: {0}".format(err))
                  pass
             else: 
                  print("Done.")
