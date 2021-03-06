class Artist(object):
    name=""
    def __init__(self, name):
        self.name=name
    def toJSON(self):
        return {"name":self.name}

class SpotifyArtist(Artist):
    spotify_uri = None
    def __init__(self, name, spotify_uri):
        super(SpotifyArtist, self).__init__(name);
        self.spotify_uri = spotify_uri
    def toJSON(self):
        json = super(SpotifyArtist, self).toJSON()
        json["spotify_uri"] = self.spotify_uri
        return json
