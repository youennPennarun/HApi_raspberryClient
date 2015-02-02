#!/usr/bin/env python

from __future__ import unicode_literals
import sys
import socket
import signal
import time
from os.path import expanduser
#import Scheduler

from hapi import Sched, Alarm, DataUtils
from server_link import RequestHandler, OnHandler, ServerHandler
#from spotify_player import SpotifyPlayer
from player import Player
from ConfigParser import SafeConfigParser

def main():

    try:
        config = SafeConfigParser()
        config.read(expanduser("~") + '/.hapi_conf')
        scheduler = Sched()
        
        def setAlarmData(data):
            print(str(data))
        print("starting node js")
        serverHandler = ServerHandler()
        
        serverHandler.on(OnHandler("alarm:new", Alarm.responseToObject))
        serverHandler.on(OnHandler("response:alarm:get", Alarm.responseToObject))
        
        serverHandler.start()
        Alarm.serverHandler = serverHandler
        
        player = Player(serverHandler, config)
        serverHandler.on(OnHandler("sound:play", player.play))
        serverHandler.on(OnHandler("sound:resume", player.resume))
        serverHandler.on(OnHandler("sound:pause", player.pause))
        serverHandler.on(OnHandler("sound:next", player.next))
        serverHandler.on(OnHandler("sound:playing:get", player.getPlayingTrack))
        serverHandler.on(OnHandler("sound:previous", player.previous))
        serverHandler.on(OnHandler("sound:volume:get", player.getVolume))
        serverHandler.on(OnHandler("sound:volume:set", player.setVolume))
        serverHandler.on(OnHandler("alarm:remove", Alarm.removeByData))
        serverHandler.on(OnHandler("alarm:update", Alarm.update))
        
        dataUtils = DataUtils(serverHandler, config)
        dataUtils.start()
        while True:
              time.sleep(0.2)
    except KeyboardInterrupt:
           player.spotifyPlayer.exit()
           sys.exit(0)
           
if __name__ == '__main__':
    sys.exit(main())

