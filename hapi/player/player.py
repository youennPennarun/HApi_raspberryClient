import sys
sys.path.append( "../server_link/" )
from spotify_player import SpotifyPlayer
from server_link import RequestHandler, OnHandler
import alsaaudio


class Player:
      spotifyPlayer = None
      def __init__(self, serverHandler, config):
          self.serverHandler = serverHandler
          sp_user = config.get('Spotify', 'username');
          sp_pwd = config.get('Spotify', 'password');
          self.spotifyPlayer = SpotifyPlayer(serverHandler, sp_user, sp_pwd)
          
      
      def play(self, data):
          self.spotifyPlayer.play(data)
      def resume(self, data):
          self.spotifyPlayer.resume(data)
      def pause(self, data):
          self.spotifyPlayer.pause(data)
      def next(self, data):
          self.spotifyPlayer.next(data)
      def previous(self, data):
          self.spotifyPlayer.previous(data)
      def getPlayingTrack(self, data):
          if self.spotifyPlayer.currentTrack is not None:
             artists = []
             for artist in self.spotifyPlayer.currentTrack.artists:
                 artists.append(artist.name)
             self.serverHandler.emit(RequestHandler("music:playing", {"track": {"name" : self.spotifyPlayer.currentTrack.name,"artist": artists}}))
          else:
             self.serverHandler.emit(RequestHandler("music:playing", {"track": {}}))
          
      def play_local(self):
          print("local")
      def getVolume(self, data):
          mixer = alsaaudio.Mixer("PCM");
          self.serverHandler.emit(RequestHandler("pi:notify:sound:volume", {"volume": mixer.getvolume()}))
      
      def setVolume(self, data):
          mixer = alsaaudio.Mixer("PCM");
          mixer.setvolume(data['volume']);
          self.serverHandler.emit(RequestHandler("pi:notify:sound:volume", {"volume": mixer.getvolume()}))
          
          