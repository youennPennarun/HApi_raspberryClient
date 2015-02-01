#!/usr/bin/env python

"""
This is an example of a simple command line client for Spotify using pyspotify.
You can run this file directly::
    python shell.py
Then run the ``help`` command on the ``spotify>`` prompt to view all available
commands.
"""

from __future__ import unicode_literals
import sys
sys.path.append( "../server_link/" )

from server_link import RequestHandler, OnHandler, ServerHandler
#from spotify_player import SpotifyPlayer
from player import Player
import logging
import time
import alsaaudio



print('Starting app.js')
serverHandler = ServerHandler()
serverHandler.start()
print('Connected to server')



player = Player(serverHandler, "nolitsou", "lazyboy29")
serverHandler.on(OnHandler("sound:play", player.play))
serverHandler.on(OnHandler("sound:resume", player.resume))
serverHandler.on(OnHandler("sound:pause", player.pause))
serverHandler.on(OnHandler("sound:next", player.next))
serverHandler.on(OnHandler("sound:previous", player.previous))
serverHandler.on(OnHandler("sound:volume:get", player.getVolume))
serverHandler.on(OnHandler("sound:volume:set", player.setVolume))
try:
    while True:
          time.sleep(0.2)
except KeyboardInterrupt:
       player.exit()
       sys.exit(0)
       
