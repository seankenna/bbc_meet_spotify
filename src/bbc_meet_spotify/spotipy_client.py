import time
from pathlib import Path
from typing import List

import spotipy
import toml
from spotipy import util

from bbc_meet_spotify.music import Music
from loguru import logger

from bbc_meet_spotify.music_not_found import MusicNotFoundError


class SpotipyClient:
    def __init__(self, config_path=Path("./config.toml")):
        config = toml.load(config_path)
        token = self._get_spotify_token(config)
        self.username = config["username"]
        self.spotipy = spotipy.Spotify(auth=token)

    @staticmethod
    def _get_spotify_token(config: dict) -> str:
        """
        If token isn't already generated, redirect to authorisation and then enter url to command line input
        :param config: configuration
        :return: spotify OAuth token
        """
        token = util.prompt_for_user_token(
            config["username"],
            "playlist-modify-private playlist-modify-public",
            config["client_id"],
            config["client_secret"],
            "http://localhost:8888",
        )
        return token

    def get_playlist(self, playlist_name: str, add_date_prefix: bool = True, public_playlist: bool = True) -> str:
        """
        Creates playlist if it doesn't already exist, otherwise get the playlist id
        :param playlist_name: name of the playlist
        :param add_date_prefix: If true, add date prefix to playlist
        :param public_playlist: if true, make the playlist public
        :return: spotify playlist
        """
        if add_date_prefix:
            playlist_name = f"{time.strftime('%Y-%m-%d')}_{playlist_name}"
        current_playlists = self.spotipy.user_playlists(self.username)

        playlist = {}
        for current_playlist in current_playlists["items"]:
            if playlist_name == current_playlist["name"]:
                playlist = current_playlist
                logger.info(f"Playlist '{playlist_name}' already exists, reusing playlist")

        if not playlist:
            logger.info(f"Creating playlist '{playlist_name}' for user '{self.username}'")
            playlist = self.spotipy.user_playlist_create(self.username, playlist_name, public=public_playlist)

        return playlist

    def add_music_to_playlist(self, playlist_id: str, music_ids: List[str]) -> None:
        """
        Music which is not currently in the playlist will be added.
        :param playlist_id: id for playlist
        :param music_ids: list of song or album ids
        :return:
        """
        playlist_info = self.spotipy.user_playlist(self.username, playlist_id, "tracks")
        existing_music = [x["track"]["id"] for x in playlist_info["tracks"]["items"]]
        new_song_ids = [music_id for music_id in music_ids if music_id not in existing_music]
        if new_song_ids:
            self.spotipy.user_playlist_add_tracks(self.username, playlist_id, new_song_ids)
        else:
            logger.info("No new music to add to the playlist")

    def get_song(self, song: Music) -> str:
        """
        Query spotify for song
        :param song: Music Object
        :raises MusicNotFoundError: if no tracks are found
        :return: spotify song
        """
        results = self.spotipy.search(q=f"artist:{song.artist} track:{song.title}")
        if not results:
            raise MusicNotFoundError()
        filtered = [result for result in results["tracks"]["items"] if song.title in result["name"].lower()]
        filtered.sort(key=lambda x: len(x["name"]))
        if not filtered:
            raise MusicNotFoundError()
        return filtered[0]

    def get_album(self, album: Music) -> List[str]:
        """
        Query spotify for album
        :param album: Music Object
        :raises MusicNotFoundError: if no tracks are found
        :return: spotify album
        """
        results = self.spotipy.search(q=f"artist:{album.artist} album:{album.title}")

        if not results:
            raise MusicNotFoundError()

        return [result for result in results["tracks"]["items"]]
