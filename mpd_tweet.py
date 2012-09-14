#! /usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


App_Name = "MPD-Tweet"
Consumer_key = "FVe1jE1h6B6ZiJ0qNoJx3g"
Consumer_secret = "CgvcbXzZ0ZN1tyYzsp8vj109OMbkVGW5UOyRFDDE1No"
Config_file = "config"

from lib.oauth_dance import oauth_dance
from lib.oauthtwitter import OAuthApi
from lib.oauth import read_token_file
from mpd import MPDClient, CommandError, MPDError
from socket import error as SocketError

import yaml

from air_utils import log_it

CONFIG = yaml.load(open("air_download.conf", "r"))


App_Name = CONFIG["twitter_app_name"]
Consumer_key = CONFIG["twitter_consumer_key"]
Consumer_secret = CONFIG["twitter_consumer_secret"]


class Tweet:
    def __init__(self):
        self.generate_config()
        self.api = self.get_twitter_access()
        
    def generate_config(self):
        try:
            f = open(Config_file)
        except IOError:
            oauth_dance(App_Name, Consumer_key, Consumer_secret, Config_file)
    
    def get_twitter_access(self):
        token = read_token_file(Config_file)
        api = OAuthApi(Consumer_key, Consumer_secret, token[0], token[1])
        return api
        
    def tweet_now_playing(self, mpdclient):
        currentSong =  mpdclient.currentsong()

        if not currentSong or currentSong['file'].startswith("jingle"):
          return

        try:
          status = ("Listening to \"%s\" by \"%s\" #nowplaying" ) % (currentSong['title'], currentSong['artist'])
        except KeyError:
          status = ("Listening to %s #nowplaying" ) % (currentSong['file'] )

        log_it("[t] %s" % (status))
        self.api.UpdateStatus(status)
        
            
    
if __name__ == "__main__":
    Tweet = Tweet()
