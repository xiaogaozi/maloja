from threading import Timer

import requests
from doreah.logging import log

from . import MetadataInterface, b64, utf


class Spotify(MetadataInterface):
    name = "Spotify"
    identifier = "spotify"

    settings = {"apiid": "SPOTIFY_API_ID", "secret": "SPOTIFY_API_SECRET"}

    metadata = {
        "trackurl": "https://api.spotify.com/v1/search?q={title}%2520artist%3A{artist}&type=track&access_token={token}&limit=50",
        "albumurl": "https://api.spotify.com/v1/search?q={title}%2520artist%3A{artist}&type=album&access_token={token}&limit=50&market=JP",
        "artisturl": "https://api.spotify.com/v1/search?q={artist}&type=artist&access_token={token}&limit=50",
        "response_type": "json",
        "response_parse_tree_track": [
            "tracks",
            "items",
            0,
            "album",
            "images",
            0,
            "url",
        ],  # use album art
        "response_parse_tree_album": ["albums", "items", 0, "images", 0, "url"],
        "response_parse_tree_artist": ["artists", "items", 0, "images", 0, "url"],
        "response_parse_track_items": ["tracks", "items"],
        "response_parse_track_item_track_name": ["name"],
        "response_parse_track_item_album_name": ["album", "name"],
        "response_parse_track_item_artist_name": ["artists", 0, "name"],
        "response_parse_track_item_imgurl": ["album", "images", 0, "url"],
        "response_parse_artist_items": ["artists", "items"],
        "response_parse_artist_item_artist_name": ["name"],
        "response_parse_artist_item_imgurl": ["images", 0, "url"],
        "response_parse_album_items": ["albums", "items"],
        "response_parse_album_item_artist_name": ["artists", 0, "name"],
        "response_parse_album_item_name": ["name"],
        "response_parse_album_item_imgurl": ["images", 0, "url"],
        "required_settings": ["apiid", "secret"],
        "enabled_entity_types": ["artist", "album", "track"],
    }

    def authorize(self):
        if self.active_metadata():
            try:
                keys = {
                    "url": "https://accounts.spotify.com/api/token",
                    "headers": {
                        "Authorization": "Basic "
                        + b64(
                            utf(self.settings["apiid"] + ":" + self.settings["secret"])
                        ).decode("utf-8"),
                        "User-Agent": self.useragent,
                    },
                    "data": {"grant_type": "client_credentials"},
                }
                res = requests.post(**keys)
                responsedata = res.json()
                if "error" in responsedata:
                    log(
                        "Error authenticating with Spotify: "
                        + responsedata["error_description"]
                    )
                    expire = 3600
                else:
                    expire = responsedata.get("expires_in", 3600)
                    self.settings["token"] = responsedata["access_token"]
                    # log("Successfully authenticated with Spotify")
                t = Timer(expire, self.authorize)
                t.daemon = True
                t.start()
            except Exception as e:
                log("Error while authenticating with Spotify: " + repr(e))

    def handle_json_result_error(self, result):
        result = result.get("tracks") or result.get("albums") or result.get("artists")
        if not result["items"]:
            return True

    def is_compilation_album(self, item):
        return item.get("album_type") == "compilation"
