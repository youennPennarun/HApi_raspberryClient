#!/usr/bin/env python

from __future__ import unicode_literals
import sys
import socket
import signal
import time
import setproctitle
import argparse
from os.path import expanduser
#import Scheduler

from hapi import Sched, Alarm, DataUtils
from server_link import RequestHandler, OnHandler, ServerHandler
#from spotify_player import SpotifyPlayer
from player import Player
from ConfigParser import SafeConfigParser
PROC_TITLE = 'HAPI client'
def get_lock(process_name):
    global lock_socket   # Without this our lock gets garbage collected
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        lock_socket.bind('\0' + process_name)
    except socket.error:
        print 'lock exists'
        sys.exit()


def main(args):
    try:
        confPath = expanduser("~") + '/.hapi_conf'
        if args.conf is not None:
           confPath = args.conf
        config = SafeConfigParser()
        config.read(confPath)
        scheduler = Sched()
        print(confPath)
        def setAlarmData(data):
            print(str(data))
        print("starting node js")
        
        if args.conf is not None:
           serverHandler = ServerHandler(confPath)
        else:
           serverHandler = ServerHandler()
        print(OnHandler)
        serverHandler.on(OnHandler("alarm:new", Alarm.responseToObject))
        serverHandler.on(OnHandler("response:alarm:get", Alarm.responseToObject))
        
        serverHandler.start()
        Alarm.serverHandler = serverHandler
        
        player = Player(serverHandler, config)
        serverHandler.on(OnHandler("sound:play", player.play))
        serverHandler.on(OnHandler("sound:resume", player.resume))
        serverHandler.on(OnHandler("sound:pause", player.pause))
        serverHandler.on(OnHandler("music:playlist:add", player.playListAdd))
        serverHandler.on(OnHandler("music:playlist:set", player.playListSet))
        serverHandler.on(OnHandler("music:playlist:get", player.playListLoad))
        serverHandler.on(OnHandler("music:player:next", player.playIdInPlaylist))
        serverHandler.on(OnHandler("music:player:previous", player.playIdInPlaylist))
        serverHandler.on(OnHandler("music:playlist:playing:id", player.playIdInPlaylist))
        serverHandler.on(OnHandler("sound:previous", player.playIdInPlaylist))
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
    get_lock(PROC_TITLE)
    setproctitle.setproctitle(PROC_TITLE)
    parser = argparse.ArgumentParser(description='Client for the HAPI server')
    parser.add_argument('--conf', help='Path to the configuration file')               
    args = parser.parse_args()
    
    sys.exit(main(args))

