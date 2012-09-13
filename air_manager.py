#!/usr/bin/env python

# IMPORTS
from mpd import (MPDClient, CommandError)
from random import choice, shuffle
from socket import error as SocketError
from sys import exit

from mpd_tweet import Tweet

import air_download
import time
import yaml
import os

## SETTINGS
##
PASSWORD = False
CONFIG = yaml.load(open("air_download.conf", "r"))
DIRECTORY = CONFIG["destination_folder"]

try:
  JINGLE_FREQUENCY = CONFIG["jingle_frequency"]
except:
  JINGLE_FREQUENCY = 2

JINGLE_DIRECTORY = CONFIG["jingle_folder"]
HOST = CONFIG["mpd_host"]
PORT = CONFIG["mpd_port"]
use_twitter = CONFIG["use_twitter"]

try:
  WAIT_SECONDS = CONFIG["email_interval"]
except:
  WAIT_SECONDS = 60
###


def mpd_connect(host, port, password=None):
  client = MPDClient()
  
  try:
    client.connect(host, port)
  except SocketError:
    raise
  
  if password:
    try:
      client.password(password)
    except CommandError:
      raise

  return client

def jingles_exist(l):
  jingles = (filter(lambda x: "jingle" in x, l))
  for jingle in jingles:
    if not os.path.isfile(os.path.join(DIRECTORY, jingle)):
      return False
  return True

def sameList(new, old):
  if len(new) is not len(old):
    return False 

  for i in range(len(new)):
    if "jingle" in new[i] and "jingle" in old[i]:
      continue
    elif not new[i] == old[i]:
      return False

  return True

jingles = os.listdir(JINGLE_DIRECTORY)
shuffle(jingles)

desired_order = sorted([f for f in os.listdir(DIRECTORY) if os.path.isfile(os.path.join(DIRECTORY, f))]) 

# add jingles
jingle_idx = 0
if jingles:
  n_songs_after_jingles = len(desired_order) + len(desired_order)/JINGLE_FREQUENCY
  for jingle_idx, j in enumerate(range(0, n_songs_after_jingles, JINGLE_FREQUENCY+1)):
    desired_order.insert(j, os.path.join("jingles", jingles[jingle_idx%len(jingles)]))

print "::: Desired order"
print "\n".join(desired_order)
print ""

client = mpd_connect(HOST, PORT)
client.repeat(1)

present_order = map(lambda x: x["file"], client.playlistinfo())

print "::: Present order"
print "\n".join(present_order)
print ""

lists_are_same = sameList(desired_order, present_order)

if not lists_are_same or not jingles_exist(present_order):
  print "::: Remaking mpd playlist"

  # store present song
  mpd_status = client.status()
  current_song = client.currentsong()

  if current_song and current_song["file"] in desired_order:
    next_song_on_new_list = (desired_order.index(current_song["file"])+JINGLE_FREQUENCY+1) % len(desired_order)
    next_song = (next_song_on_new_list / (JINGLE_FREQUENCY+1)) * (JINGLE_FREQUENCY+1)
  else:
    next_song = 0

  # remake list
  client.clear()
  client.update()
  time.sleep(5)
  for i in desired_order:
    print "[+] adding %s" % (i)
    client.add(i)

  # fast forward to next advertisement... (abrupt kill)
  if len(client.playlistinfo()):
    print "[>] pressing play"
    client.play(next_song)

if use_twitter:
  tweetManager = Tweet()
  print "::: Twitter is in use"

mpd_status = client.status()
print "[?] mpd state:", mpd_status["state"]

client.disconnect()

previousSong = None

while True:
  client = mpd_connect(HOST, PORT)

  if use_twitter:
    currentSong = client.currentsong()
    if not previousSong == currentSong:
      try:
        tweetManager.tweet_now_playing(client)
      except:
        print "::: Tweeting failed"
      previousSong = currentSong

  new_files = air_download.ezrun()

  if new_files:
    print "::: %d new file(s) found" % (len(new_files))
    for filename in new_files:
      client.update()
      time.sleep(5) # allow for the update to happen

      # check if we should add a jingle now
      if jingles and (len(client.playlistinfo()) % (JINGLE_FREQUENCY+1)) == 0:
        jingle_idx = jingle_idx+1
        jingle = jingles[jingle_idx%len(jingles)]
        print "[+] add %s" % (jingle)
        client.add(os.path.join("jingles", jingle))

      print "[+] add %s" % (filename)
      client.add(filename) 

    # in case the station is stopped and receives its first song
    if not client.status()["state"] == "play" and len(client.playlistinfo()):
      print "[>] pressing play"
      client.play(0)

  client.disconnect()
  time.sleep(WAIT_SECONDS)

