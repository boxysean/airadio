#!/usr/bin/env python

# IMPORTS
from mpd import (MPDClient, CommandError)
from random import choice
from socket import error as SocketError
from sys import exit

import air_download
import time
import yaml
import os

## SETTINGS
##
HOST = 'localhost'
PORT = '6600'
PASSWORD = False
WAIT_SECONDS = 60
CONFIG = yaml.load(open("air_download.yml", "r"))
DIRECTORY = CONFIG["destination_folder"]
###


client = MPDClient()

try:
    client.connect(host=HOST, port=PORT)
except SocketError:
    exit(1)

if PASSWORD:
    try:
        client.password(PASSWORD)
    except CommandError:
        exit(1)

client.clear()
client.stop()

for f in os.listdir(DIRECTORY):
  print "[+] adding %s" % (f)
  client.add(f)

try:
  while True:
    air_download.ezrun(lambda x: client.update and client.add(x))
    time.sleep(WAIT_SECONDS)
except:
  print "exiting gracefully"
  
client.disconnect()


