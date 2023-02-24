from typing import List, Set

from loguru import logger

from bbc_meet_spotify.music import Music
from bbc_meet_spotify.music_not_found import MusicNotFoundError
from bbc_meet_spotify.spotipy_client import SpotipyClient


class Spotify:
    def __init__(self):
        self.spotipy_client = SpotipyClient()
        self.music_not_found = []

    def add_albums(self, playlist_name: str, albums: Set[Music], add_date_prefix=True, public_playlist=True) -> None:
        """
        Adds albums to Spotify playlist
        :param playlist_name: name of the playlist to be created or appended to
        :param albums: albums to be added
        :param add_date_prefix: If true, add date prefix to playlist
        :param public_playlist: If true, make playlist public
        """
        playlist_id = self.spotipy_client.get_playlist(playlist_name, add_date_prefix, public_playlist)["id"]
        album_ids = []
        for album in albums:
            try:
                album_ids.extend(self.spotipy_client.get_album(album)["id"])
            except MusicNotFoundError:
                self.music_not_found.append(album.to_string())
                break
            self.spotipy_client.add_music_to_playlist(playlist_id, album_ids)

        self._log_music_not_found()

    def add_songs(self, playlist_name: str, songs: Set[Music], add_date_prefix=True, public_playlist=True) -> None:
        """
        Adds songs to Spotify playlist
        :param playlist_name: name of the playlist to created or appended to
        :param songs: songs to be added
        :param add_date_prefix: If true, add date prefix to playlist
        :param public_playlist: If true, make playlist public
        """
        playlist_id = self.spotipy_client.get_playlist(playlist_name, add_date_prefix, public_playlist)["id"]
        song_ids = self._get_song_ids(songs)
        if not self.music_not_found:
            self.spotipy_client.add_music_to_playlist(playlist_id, song_ids)

        self._log_music_not_found()

    def _get_song_id(self, song: Music) -> str:
        """
        Get Spotify song id
        First queries Spotify with unsanitised track details
        Second queries spotify with sanitised track details
        If not found, appends to not found list
        :param song: song to lookup
        :return: song_id
        """
        try:
            return self.spotipy_client.get_song(song)["id"]
        except MusicNotFoundError:
            try:
                song = song.sanitize()
                return self.spotipy_client.get_song(song)
            except MusicNotFoundError:
                self.music_not_found.append(f"{song.to_string()}")

    def _get_song_ids(self, songs: List[Music]) -> List[str]:
        """
        Get list of Spotify song ids
        :param songs: list of songs to search
        :return: list of song ids
        """
        return [self._get_song_id(song) for song in songs]

    def _log_music_not_found(self) -> None:
        message_base = "All done!"
        if self.music_not_found:
            not_found = "\n\t".join(self.music_not_found)
            logger.info(f"{message_base}\n"
                        f"Couldn't find the following music, you'll have to do this manually for now 😥\n\t"
                        f"{not_found}")
        else:
            logger.info(f"{message_base} No music needs to be added manually 🥳")
