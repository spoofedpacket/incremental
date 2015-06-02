#!/usr/bin/python

'''
incremental.py:

 Carries out incremental backups of one folder to another, using
 rsync and hardlinks. Intended to be run daily, after midnight.

'''

__author__ = "Robert Gallagher"
__version__ = "0.4"

##############################################################################################
# System modules.
##############################################################################################
import os
import string
import subprocess
import sys
import datetime
import time

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
      def doBackup(src, dst, prev, rsync_opts):
          dst_tree = os.path.join(dst, "tree")
          if not os.path.exists(dst_tree):
             try:
                print("INFO: Backup target directory " + dst_tree + " doesn't exist, creating it.\n")
                os.makedirs(dst_tree)
             except OSError as e:
                print("ERROR: Could not create backup directory!: {0}".format(e))
          prev_tree = os.path.join(prev, "tree")
          finish_file = os.path.join(dst, "backup.done")
          start_time = time.time()
          start_time_s = time.ctime(start_time)
          try:
             print("** Backup of " + src + " started at " + start_time_s)
             print("*** Backing up to " + dst_tree)
             print("*** Hardlinking to " + prev_tree + "\n")
             subprocess.check_call(["rsync", rsync_opts, "--numeric-ids", "--stats", "--delete-delay", "--link-dest=" + prev_tree, src, dst_tree])
          except subprocess.CalledProcessError as e:
             print("ERROR: rsync error: {0}".format(e))
          finish_time = time.time()
          finish_time_s = time.ctime(finish_time)
          print("\n** Backup of " + src + " ended at " + finish_time_s + "\n")
          try:
              f = open(finish_file, 'w')
              f.write(str(finish_time))
              f.close()
          except IOError as e:
             print("ERROR: Could not write out timestamp: {0}".format(e))

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
   try:
      with open(CFG, 'r') as ymlfile:
          cfg = yaml.load(ymlfile)
   except IOError as e:
          print("ERROR: Could not read configuration!: {0}".format(e))

   # Check if we're in dry run mode 
   if TEST:
     rsync_opts = "-vrltHpgoDn"
   else:
     rsync_opts = "-vrltHpgoD"

   backup_root = os.path.join(cfg['backup_root'], '')

   backup_locations = cfg['backup_locations']
     
   # Generate some timestamps
   today = datetime.datetime.today()
   yesterday = datetime.datetime.today() - datetime.timedelta(1)
   today_s = today.strftime("%Y%m%d")
   yesterday_s = yesterday.strftime("%Y%m%d")
   now = datetime.datetime.now()
   now_s = now.strftime("%c")

   for name, path in backup_locations.items():
      source_path = os.path.join(backup_locations[name]['path'], '')
      target_path_root = os.path.join(backup_root, name, 'backups')
      if not os.path.exists(target_path_root):
         try:
            print("INFO: Backup root directory " + target_path_root + " doesn't exist, creating it.\n")
            os.makedirs(target_path_root)
         except OSError as e:
            print("ERROR: Could not create backup root directory!: {0}".format(e))
      target_path_today = os.path.join(target_path_root, today_s)
      # Check if previous day's backup has been archived and adjust the hardlink path accordingly
      if not os.path.exists(os.path.join(target_path_root, yesterday_s)):
         if os.path.exists(os.path.join(backup_root, name, 'archive', 'weekly', yesterday_s)):
            target_path_yesterday = os.path.join(backup_root, name, 'archive', 'weekly', yesterday_s)
         elif os.path.exists(os.path.join(backup_root, name, 'archive', 'monthly', yesterday_s)):
            target_path_yesterday = os.path.join(backup_root, name, 'archive', 'monthly', yesterday_s)
         else:
            print("\nINFO: Could not determine path to previous backup for hardlinking. A full backup will commence.\n")
            target_path_yesterday = os.path.join(target_path_root, 'nonexistent')
      else:
         target_path_yesterday = os.path.join(target_path_root, yesterday_s)
      incremental.doBackup(source_path, target_path_today, target_path_yesterday, rsync_opts)
      try:
         os.unlink(target_path_root + "/" + "latest")
      except OSError as e:
         print("\nERROR: Could not delete symlink to previous backup: {0}".format(e))
      try:
         os.symlink(target_path_today, target_path_root + "/" + "latest")
      except OSError as e:
         print("\nERROR: Could not create symlink to previous backup: {0}".format(e))

