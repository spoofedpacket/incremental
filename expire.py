#!/usr/bin/python

'''
expire.py:

 Examines the backup directory tree, archives old backups and deletes any backups
 that are expired. Should be run after incremental.py.

'''

__author__ = "Robert Gallagher"
__version__ = "0.4"

# Modules
import os
import time
import datetime
import shutil
import string
import argparse
import yaml

class expire:
      @staticmethod
      def archiveBackup(expire_backup_dir, expire_archive_monthly, expire_archive_weekly):
          d = datetime.datetime
          for dir in os.listdir(expire_backup_dir):
              full_path = os.path.join(expire_backup_dir, dir)
              if os.path.isdir(full_path):
                # Read the timestamp from the backup.done file (epoch seconds)
                try:
                   f = open(full_path + "/backup.done", 'r')
                except IOError as e:
                   print("ERROR: Could not read backup.done file: {0}".format(e))
                ts_from_file = f.readline()
                f.close()
                timestamp = float(ts_from_file)
                timestamp_d = d.fromtimestamp(timestamp)
                # Archive weekly backups (end of the week is Sunday)
                if timestamp_d.isoweekday() == 7:
                    try:
                         if TEST:
                           print("TEST: Would archive " + full_path)
                         else:
                           print("Archiving weekly backup " + full_path)
                           shutil.move(full_path, expire_archive_weekly)
                           expire.updateSymlink(expire_backup_dir, expire_archive_weekly + "/" + os.path.basename(full_path))
                    except Exception as e:
                         print("ERROR: Couldn't move directory!: {0}".format(e))
                         pass
                # Archive monthly backups (first of the month)
                if timestamp_d.day == 1:
                    try:
                         if TEST:
                           print("TEST: Would archive " + full_path)
                         else:
                           print("Archiving monthly backup " + full_path)
                           shutil.move(full_path, expire_archive_monthly)
                           expire.updateSymlink(expire_backup_dir, expire_archive_monthly + "/" + os.path.basename(full_path))
                    except Exception as e:
                         print("ERROR: Couldn't move directory!: {0}".format(e))
                         pass
      @staticmethod
      def expireBackup(backup_dir, now, max_age):
          d = datetime.datetime
          if max_age != 0:
            for dir in os.listdir(backup_dir):
              full_path = os.path.join(backup_dir, dir)
              if os.path.isdir(full_path):
                # Read the timestamp from the backup.done file (epoch seconds)
                try:
                   f = open(full_path + "/backup.done", 'r')
                except IOError as e:
                   print("ERROR: Could not read backup.done file: {0}".format(e))
                ts_from_file = f.readline()
                f.close()
                timestamp = float(ts_from_file)
                timestamp_d = d.fromtimestamp(timestamp)
                # Round the timestamp to the nearest day
                timestamp_d_rnd = timestamp_d.replace(hour=0, minute=0, second=0, microsecond=0)
                timestamp_f_rnd = float((timestamp_d_rnd - datetime.datetime(1970,1,1)).total_seconds())
                if now-max_age > timestamp_f_rnd:
                    try:
                         if TEST:
                           print("TEST: Would remove " + full_path)
                         else:
                           print("Removing " + full_path)
                           shutil.rmtree(full_path)
                    except Exception as e:
                         print("ERROR: Couldn't remove directory!: {0}".format(e))
                         pass
          elif max_age == 0:
            return
      @staticmethod
      def updateSymlink(backup_dir, new_path):
          try:
              os.unlink(backup_dir + "/" + "latest")
          except OSError as e:
              print("\nERROR: Could not delete symlink to previous backup: {0}".format(e))
          try:
              os.symlink(new_path, backup_dir + "/" + "latest")
          except OSError as e:
              print("\nERROR: Could not create symlink to previous backup: {0}".format(e))


if __name__ == "__main__":
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
          print ("ERROR: Could not read configuration!: {0}".format(e))
   
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
   
   # Process each backup directory.
   for name, path in backup_locations.items():
      expire_root_dir = os.path.join(backup_root, name, '')
      expire_archive_dir = os.path.join(expire_root_dir, 'archive')
      expire_backup_dir = os.path.join(expire_root_dir, 'backups')
      expire_archive_weekly = os.path.join(expire_archive_dir, 'weekly')
      expire_archive_monthly = os.path.join(expire_archive_dir, 'monthly')
      if not os.path.exists(expire_archive_dir):
         try:
            print("INFO: Archive directory " + expire_archive_dir + " doesn't exist, creating it.\n")
            os.makedirs(expire_archive_dir)
            os.makedirs(os.path.join(expire_archive_dir, 'monthly'))
            os.makedirs(os.path.join(expire_archive_dir, 'weekly'))
         except OSError as e:
            print("ERROR: Could not create archive directory!: {0}".format(e))
      expire.archiveBackup(expire_backup_dir, expire_archive_monthly, expire_archive_weekly)
      expire.expireBackup(expire_backup_dir, now, expire_default)
      expire.expireBackup(expire_archive_weekly, now, expire_weekly)
      expire.expireBackup(expire_archive_monthly, now, expire_monthly)

