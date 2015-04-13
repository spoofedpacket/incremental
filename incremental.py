#!/usr/bin/python

'''
incremental.py:

 Carries out incremental backups of one folder to another, using
 rsync and hardlinks. Intended to be run daily, after midnight.

'''

__author__ = "Robert Gallagher"
__version__ = "0.1"

##############################################################################################
# System modules.
##############################################################################################
import os
import string
import subprocess
import sys
import datetime

##############################################################################################
# 3rd-party modules.
##############################################################################################
import argparse
import yaml

##############################################################################################
# Main class.
##############################################################################################
class incremental:
      @staticmethod
      def doBackup(src, dst, today_s, yesterday_s, rsync_opts):
          current = dst + "/" + today_s
          previous = dst + "/" + yesterday_s 
          subprocess.check_call(["rsync", rsync_opts, "--numeric-ids", "--stats", "--delete-delay", "--link-dest=" + previous, src, current]) 

##############################################################################################
# Default invocation.
##############################################################################################
if __name__ == "__main__":
   # Process command line arguments
   argparser = argparse.ArgumentParser()
   argparser.add_argument('-c', action='store', dest='CFG', help='Config file location (defaults to /usr/local/etc/incremental.yaml)')
   argparser.add_argument('-t', action='store_true', dest='TEST', help='Run in test mode. Show what would be backed up.')
   arguments  = argparser.parse_args()
   CFG = arguments.CFG
   TEST = arguments.TEST

   # Ensure CFG is set, if the user hasn't supplied it
   if CFG == None:
      CFG = "/usr/local/etc/incremental.yaml"

   # Process config
   with open(CFG, 'r') as ymlfile:
       cfg = yaml.load(ymlfile)

   # Check if we're in dry run mode 
   if TEST:
     rsync_opts = "-vrltHpgoDn"
   else:
     rsync_opts = "-vrltHpgoD"

   backup_root = cfg['backup_root']

   backup_locations = cfg['backup_locations']
     
   today = datetime.date.today()
   yesterday = datetime.date.today() - datetime.timedelta(1)
   today_s = today.strftime("%Y%m%d")
   yesterday_s = yesterday.strftime("%Y%m%d")

   for name, path in backup_locations.iteritems():
      incremental.doBackup(backup_locations[name]['path'], backup_root + name, today_s, yesterday_s, rsync_opts)

