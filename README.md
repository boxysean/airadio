Autonomous Interactive Radio
============================

A radio station manager program that queues and plays all songs (mp3s, m4as, etc.) received by email.

![air cycle](http://dump.boxysean.com/air-cycle.png)

Requirements
------------

Tested on Ubuntu 11.04 and with python versions 2.7.1 and 2.7.3. See `requirements.txt` for required python libraries and versions.

Features
--------

* Uses [`mpd`](http://en.wikipedia.org/wiki/Music_Player_Daemon) to play music
* Ability to add jingles between songs!
* "Now playing" Twitter feed
* Email response for successful submissions

Debian installation instructions
--------------------------------

1. `apt-get install pip mpd mpc`
2. `pip install -U -r requirements.txt
3. `git clone git@github.com:boxysean/airadio.git`
4. `cp air_download.conf.sample air_download.conf`
5. Edit `air_download.conf` (suggest making a new email account for this)
4. `python air_manager.py`

To make this a service on startup ([from here](http://www.debian-administration.org/articles/28)):

1. Edit `AIR_DIR` variable in `init.d/airadio`
2. `sudo cp init.d/airadio /etc/init.d/`
3. `update-rc.d airadio defaults`

Outputting to FM broadcast transmitter
--------------------------------------

This project can be paired with an FM transmitter to create a community pirate radio station. We ran this software on a Raspberry Pi paired with a low-power FM transmitter, [see more](http://heartheair.tumblr.com/).

Streaming to an Icecast server
------------------------------

`mpd` has built in functionality to stream what it plays to an Icecast server. This gives you the option to stream Autonomous Interactive Radio to your friends via the Internet. [Learn how to do this](http://www.omskakas.se/2006/06/your-own-internet-radio-station-with-mpdicecast.html).

[Learn how to do this on a Raspberry Pi](http://www.t3node.com/blog/streaming-audio-with-mpd-and-icecast2-on-raspberry-pi/), but I warn you that the Raspi is CPU-bound when it does this and tends to have choppy playback.
