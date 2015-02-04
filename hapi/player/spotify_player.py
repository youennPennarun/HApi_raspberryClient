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
from operator import itemgetter


class SpotifyPlayer():
    idPlaying = 0
    playlist = []
    doc_header = 'Commands'
    prompt = 'spotify> '

    logger = logging.getLogger('shell.commander')

    def __init__(self, serverHandler, username = None, password = None):
        self.serverHandler = serverHandler
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
           self.notifyPlaying(None)

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
    def play_next(self):
        if not self.logged_in.is_set():
            self.logger.warning('You must be logged in to play')
            return False
        try:
            #session.relogin()
            print("play id "+str(self.idPlaying))
            if len(self.playlist) > self.idPlaying:
               track = self.session.get_track(self.playlist[self.idPlaying]['link']['uri'])
               track.load()
            else:
                 return False
        except (ValueError, spotify.Error) as e:
            self.logger.warning(e)
            return False
        self.logger.info('Loading track into player')
        try:
            self.session.player.load(track)
            self.notifyPlaying(track)
            self.logger.info('Playing track')
            self.session.player.play()
            return True
        except (ValueError, spotify.Error) as e:
            self.logger.warning(e)
            self.logger.info(self.playlist[self.idPlaying])
            return False
               
        
    def notifyPlaying(self, track):
        self.currentTrack = track
        if self.currentTrack is not None:
             artists = []
             for artist in self.currentTrack.artists:
                 artists.append(artist.name)
             self.serverHandler.emit(RequestHandler("music:playing", {"track": {"name" : self.currentTrack.name,"artist": artists}}))
        else:
           self.serverHandler.emit(RequestHandler("music:playing", {"track": {}}))
    def play_trackset(self, data):
        self.playlist = data['tracks'];
        self.play_uri(playlist[0])
        
    def play(self, data):
        if data['type'] == "track":
           self.idPlaying = 0
           self.playlist = [];
           self.playlist.append(data['track']);
           self.play_next()
        elif data['type'] == "trackset":
           self.idPlaying = 0
           self.playlist = [];
           if 'tempoId' in data['track']: 
              for track  in (sorted(data['track'], key=itemgetter('tempoId'))):
                  self.playlist.append(track);
           else:
                self.playlist = data['track']
           self.play_next()
        elif data['type'] == "search":
           results = self.search(data['search'])
           self.idPlaying = 0
           self.playlist = [];
           self.playlist = results;
           self.play_next()
           
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
        player.login("nolitsou", "lazyboy29")
        player.play_uri("spotify:track:22e6sT2Pu8kXpJeItO0xGg")
        while True:
              time.sleep(0.2)
    except KeyboardInterrupt:
           player.exit()
           sys.exit(0)
