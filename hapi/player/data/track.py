class Track(object):
    name=""
    artists=[]
    def __init__(self, name, artists):
        self.name=name
        self.artists=artists
        if artists is None:
            self.artists=[]
    def toJSON(self):
        json = {"name": self.name}
        json["artists"] = []
        for artist in self.artists:
            json["artists"].append(artist.toJSON());
        return json
class SpotifyTrack(Track):
    spotify_id = None
    spotify_uri = None
    def __init__(self,spotify_id, name, artists, spotify_uri):
        super(SpotifyTrack, self).__init__(name, artists)
        self.spotify_id = spotify_id
        self.spotify_uri = spotify_uri	
    def toJSON(self):
        json = super(SpotifyTrack, self).toJSON()
        json["spotify_id"] = self.spotify_id
        json["spotify_uri"] = self.spotify_uri
        print(json)
        return json
