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
from server_link import RequestHandler, OnHandler
import logging
import threading
import time
import spotify
import sys
from os.path import expanduser
from operator import itemgetter
from data import *


class SpotifyPlayer():
    idPlaying = 0
    playlist = []
    doc_header = 'Commands'
    prompt = 'spotify> '

    logger = logging.getLogger('shell.commander')

    def __init__(self, serverHandler, username = None, password = None):
        self.serverHandler = serverHandler
	hdlr = logging.FileHandler(expanduser("~")+'/hapi.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr) 
        self.logger.setLevel(logging.INFO)
        self.logged_in = threading.Event()
        self.logged_out = threading.Event()
        self.logged_out.set()
        self.logger.info('Initializing player')

        self.session = spotify.Session()
        self.session.on(
            spotify.SessionEvent.CONNECTION_STATE_UPDATED,
            self.on_connection_state_changed)
        self.session.on(
            spotify.SessionEvent.END_OF_TRACK, self.on_end_of_track)

        try:
            self.audio_driver = spotify.AlsaSink(self.session)
        except ImportError:
            self.logger.warning(
                'No audio sink found; audio playback unavailable.')

        self.event_loop = spotify.EventLoop(self.session)
        self.event_loop.start()
        if username is not None and password is not None:
           self.login(username, password)
        self.logger.info('Ready')
        self.currentTrack = None


    def on_connection_state_changed(self, session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in.set()
            self.logged_out.clear()
        elif session.connection.state is spotify.ConnectionState.LOGGED_OUT:
            self.logged_in.clear()
            self.logged_out.set()

    def on_end_of_track(self, session):
        self.idPlaying = self.idPlaying+1;
        if len(self.playlist) > self.idPlaying:
           self.play_next()
        else:
           self.session.player.play(False)

    def exit(self):
        if self.logged_in.is_set():
            print('Logging out...')
            self.session.logout()
            self.logged_out.wait()
        self.event_loop.stop()
        print('')
        return True

    def login(self, username, password):
        self.session.login(username, password, remember_me=True)
        self.logged_in.wait()

    def relogin(self):
        try:
            self.session.relogin()
            self.logged_in.wait()
        except spotify.Error as e:
            self.logger.error(e)

    def forget_me(self):
        self.session.forget_me()

    def logout(self):
        self.session.logout()
        self.logged_out.wait()

    def play_uri(self, track_uri):
        if not self.logged_in.is_set():
            self.logger.warning('You must be logged in to play')
            return
        try:
            track = self.session.get_track(track_uri)
            track.load()
        except (ValueError, spotify.Error) as e:
            self.logger.warning(e)
            return
        self.logger.info('Loading track into player')
        self.session.player.load(track)
        self.logger.info('Playing track')
        self.session.player.play()
    def playIdInPlaylist(self, data):
        print(data)
        self.idPlaying = data['idPlaying']
        self.play(self.playlist[self.idPlaying])
        
    def play_next(self):
        self.idPlaying += 1
        if len(self.playlist) > self.idPlaying:
            self.play(self.playlist[self.idPlaying])
        else:
            self.idPlaying = 0
            self.currentTrack = None
            return False
    def play_trackset(self, data):
        self.playlist = data['tracks'];
        self.play_uri(playlist[0])
    def playListLoad(self, data):
        self.playlist = []
        self.currentTrack = None
        self.playListAdd({"type": "trackset", "tracks": data["playlist"]}, False)
        self.idPlaying = data['idPlaying']
        if self.idPlaying < 0:
            self.idPlaying = 0
            
        
    def playListSet(self, data):
        self.playlist = []
        self.currentTrack = None
        self.playListAdd(data)
    def playListAdd(self, data, autoplay=True):
        if data['type'] == "track":
            self.playlist.append(data['track']['spotifyData']['uri'])
            self.logger.info('Adding in playlist 1 track')
        elif data['type'] == "trackset":
            self.logger.info('Adding in playlist '+str(len(data['tracks']))+' track')
            for track in data['tracks']:
                self.playlist.append(track['spotifyData']['uri'])
        if self.currentTrack is None and autoplay:
            self.idPlaying = 0
            self.play(self.playlist[self.idPlaying])

    def play(self, trackUri=None):
        self.logger.info("playing uri " + trackUri)
        if not self.logged_in.is_set():
            self.logger.warning('You must be logged in to play')
            return False
        try:
            self.currentTrack = self.session.get_track(trackUri)
            self.currentTrack.load()
            print("Ready to play" + self.currentTrack.name);
        except (ValueError, spotify.Error) as e:
            self.logger.warning(e)
            return False
        self.logger.info('Loading track into player')
        try:
            self.session.player.load(self.currentTrack)
            self.logger.info('Playing track')
            self.session.player.play()
            self.serverHandler.emit(RequestHandler("music:playlist:playing:setId", {'idPlaying':self.idPlaying}))
            return True
        except (ValueError, spotify.Error) as e:
            self.logger.warning(e)
            return False
           
    def search(self, searchInfo):
        results = []
        result = None
        print(searchInfo['type'])
        if searchInfo['type'] == 'trackset':
           for search in searchInfo['data']:
               print(search);
               result = self.execute_search('artist:"%s" title:"%s"' % (search['artist_name'], search['title']))
               if result is not None:
                  print("--------------------")
                  print(result);
                  print("--------------------")
                  results.append(result)
        return results
               
    
    def execute_search(self, query):
        resultTrack = None
        if not self.logged_in.is_set():
            self.logger.warning('You must be logged in to search')
            return
        try:
            result = self.session.search(query)
            result.load()
        except spotify.Error as e:
            self.logger.warning(e)
            return
        if result.track_total > 0:
           resultTrack = {'uri': result.tracks[0].link.uri, 'name': result.tracks[0].name}
        return resultTrack
               
           
                           
    def pause(self, data):
        self.logger.info('Pausing track')
        self.session.player.play(False)

    def resume(self, data):
        if self.currentTrack is None:
            if len(self.playlist) > 0:
                self.idPlaying = 0
                self.play(self.playlist[self.idPlaying])
        else:
            self.logger.info('Resuming track')
            self.session.player.play()

    def stop(self, data):
        self.logger.info('Stopping track')
        self.session.player.play(False)
        self.session.player.unload()
    def next(self, data):
        if len(self.playlist) > (self.idPlaying +1) :
            self.idPlaying  = self.idPlaying + 1
            self.play_next()
    def previous(self, data):
        if self.idPlaying > 0  :
            self.idPlaying  = self.idPlaying - 1
            self.play_next()
            
        
        

    def seek(self, seconds):
        if not self.logged_in.is_set():
            self.logger.warning('You must be logged in to play')
            return
        # TODO Check if playing
        self.session.player.seek(int(seconds) * 1000)



if __name__ == '__main__':
    serverHandler = ServerHandler()
    logging.basicConfig(level=logging.INFO)
    player = SpotifyPlayer()
    try:
        player.play_uri("spotify:track:22e6sT2Pu8kXpJeItO0xGg")
        while True:
              time.sleep(0.2)
    except KeyboardInterrupt:
           player.exit()
           sys.exit(0)
