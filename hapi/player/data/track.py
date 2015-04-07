class Track(object):
    title=""
    artist=None
    def __init__(self, title, artist):
	self.title=title
	self.artist=artist

class SpotifyTrack(Track):
    spotify_id = None
    spotify_uri = None
    def __init__(self,spotify_id, title, artist, spotify_uri):
        super(SpotifyTrack, self).__init__(title, artist)
        self.spotify_id = spotify_id
        self.spotify_uri = spotify_uri	
