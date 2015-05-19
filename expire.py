#!/usr/bin/python
import os
import time
import shutil
import string
import argparse
import yaml
expired = 86400*15
now = time.time()

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
except IOError,e:
       print e

backup_root = os.path.join(cfg['backup_root'], '')

backup_locations = cfg['backup_locations']

for name, path in backup_locations.items():
   expire_root_dir = os.path.join(backup_root, name, '')
   for r,d,f in os.walk(expire_root_dir):
       for dir in d:
         timestamp = os.path.getmtime(os.path.join(r,dir))
         if now-expired > timestamp:
             try:
                  if TEST:
                    print "Would remove ",os.path.join(r,dir)
                  else:
                    print "Removing ",os.path.join(r,dir)
                    #shutil.rmtree(os.path.join(r,dir))  #uncomment to use
             except Exception,e:
                  print e
                  pass
             else: 
                  print "Done."
