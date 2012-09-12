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
HOST = 'boxysean.com'
PORT = '6600'
PASSWORD = False
WAIT_SECONDS = 5
CONFIG = yaml.load(open("air_download.yml", "r"))
DIRECTORY = CONFIG["destination_folder"]
###


client = MPDClient()

try:
    client.connect(host=HOST, port=PORT)
except SocketError:
    raise

if PASSWORD:
    try:
        client.password(PASSWORD)
    except CommandError:
        raise

client.clear()
client.stop()
client.update()

for f in sorted(os.listdir(DIRECTORY)):
  print "[+] adding %s" % (f)
  client.add(f)

client.disconnect()

while True:
  air_download.ezrun(client)
  time.sleep(WAIT_SECONDS)
