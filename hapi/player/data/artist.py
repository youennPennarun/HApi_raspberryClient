class Artist(object):
    name=""
    def __init__(self, name):
	self.name=name

class SpotifyArtist(Artist):
    spotify_uri = None
    def __init__(self, name, spotify_uri):
	super(SpotifyArtist, self).__init__(name);
	self.spotify_uri = spotify_uri
	
