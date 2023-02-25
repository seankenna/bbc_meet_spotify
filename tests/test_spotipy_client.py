import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from bbc_meet_spotify import MusicNotFoundError
from bbc_meet_spotify.music import Music
from bbc_meet_spotify.spotipy_client import SpotipyClient


def _read_file_as_json(file_path: str) -> json:
    with open(file_path) as json_data:
        return json.load(json_data)


class TestSpotipyClient:
    def setup(self):
        self.resources_ = Path(__file__).parent / "resources"
        self.config = self.resources_ / "config.toml"

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_add_music_to_playlist_when_no_new_song_ids_then_returns(self, mock_spotify_client: MagicMock,
                                                                     mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.user_playlist.return_value = _read_file_as_json(
            f"{self.resources_}/spotipy/input/get_playlist.json")
        spotipy_client = SpotipyClient(config_path=self.config)
        spotipy_client.add_music_to_playlist("test-playlist-id", ["1", "2", "3"])
        mock_spotify_client_instance.user_playlist_add_tracks.assert_not_called()

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_add_music_to_playlist_when_new_song_ids_then_adds_tracks(self, mock_spotify_client: MagicMock,
                                                                      mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.user_playlist.return_value = _read_file_as_json(
            f"{self.resources_}/spotipy/input/get_playlist.json")
        spotipy_client = SpotipyClient(config_path=self.config)
        spotipy_client.add_music_to_playlist("test-playlist-id", ["5", "6"])
        mock_spotify_client_instance.user_playlist_add_tracks.assert_called_with("bbc_meet_spotify",
                                                                                 "test-playlist-id", ["5", "6"])

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    @patch("bbc_meet_spotify.spotipy_client.time.strftime", return_value="2013-02-01")
    def test_get_playlist_when_playlist_exists_then_returns_existing_playlist(self, mock_time: time,
                                                                              mock_spotify_client: MagicMock,
                                                                              mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.user_playlists.return_value = _read_file_as_json(
            f"{self.resources_}/spotipy/input/get_users_playlists.json")
        spotipy_client = SpotipyClient(config_path=self.config)
        playlist = spotipy_client.get_playlist("test-playlist-id")
        mock_spotify_client_instance.user_playlists.is_called_with("2013-02-01_test-playlist-id")
        mock_spotify_client_instance.user_playlist_create.assert_not_called()
        assert playlist == _read_file_as_json(
            f"{self.resources_}/spotipy/output/get_playlist.json")

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_get_playlist_when_playlist_new_then_returns_new_playlist(self, mock_spotify_client: MagicMock,
                                                                      mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.user_playlists.return_value = _read_file_as_json(
            f"{self.resources_}/spotipy/input/get_users_playlists.json")
        mock_spotify_client_instance.user_playlist_create.return_value = _read_file_as_json(
            f"{self.resources_}/spotipy/input/create_playlist.json")
        spotipy_client = SpotipyClient(config_path=self.config)
        playlist = spotipy_client.get_playlist("new-playlist", False)
        mock_spotify_client_instance.user_playlist_create.assert_called_with("bbc_meet_spotify", "new-playlist",
                                                                             public=True)
        assert playlist == _read_file_as_json(
            f"{self.resources_}/spotipy/input/create_playlist.json")

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_get_playlist_when_playlist_new_then_returns_new_private_playlist(self, mock_spotify_client: MagicMock,
                                                                              mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.user_playlists.return_value = _read_file_as_json(
            f"{self.resources_}/spotipy/input/get_users_playlists.json")
        mock_spotify_client_instance.user_playlist_create.return_value = _read_file_as_json(
            f"{self.resources_}/spotipy/input/create_playlist.json")
        spotipy_client = SpotipyClient(config_path=self.config)
        playlist = spotipy_client.get_playlist("new-playlist", False, False)
        mock_spotify_client_instance.user_playlist_create.assert_called_with("bbc_meet_spotify", "new-playlist",
                                                                             public=False)
        assert playlist == _read_file_as_json(
            f"{self.resources_}/spotipy/input/create_playlist.json")

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_get_song(self, mock_spotify_client: MagicMock, mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.search.return_value = _read_file_as_json(
            f"{self.resources_}/spotipy/input/search.json")
        spotipy_client = SpotipyClient(config_path=self.config)
        track_id = spotipy_client.get_song(Music("artist", "title"))
        mock_spotify_client_instance.search.assert_called_with(q="artist:artist track:title")
        assert track_id == _read_file_as_json(
            f"{self.resources_}/spotipy/output/get_song.json")

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_get_song_when_no_search_results_throws(self, mock_spotify_client: MagicMock,
                                                    mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.search.return_value = []
        spotipy_client = SpotipyClient(config_path=self.config)
        try:
            spotipy_client.get_song(Music("artist", "title"))
        except MusicNotFoundError:
            pass

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_get_song_when_no_match_results_throws(self, mock_spotify_client: MagicMock,
                                                   mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.search.return_value = _read_file_as_json(
            f"{self.resources_}/spotipy/input/search.json")
        spotipy_client = SpotipyClient(config_path=self.config)
        try:
            spotipy_client.get_song(Music("no-match-artist", "no-match-title"))
        except MusicNotFoundError:
            pass

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_get_album(self, mock_spotify_client: MagicMock, mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.search.return_value = _read_file_as_json(
            f"{self.resources_}/spotipy/input/search.json")
        spotipy_client = SpotipyClient(config_path=self.config)
        tracks = spotipy_client.get_album(Music("title", "artist"))
        mock_spotify_client_instance.search.assert_called_with(q="artist:title album:artist")
        assert tracks == _read_file_as_json(
            f"{self.resources_}/spotipy/output/get_album.json")

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_get_album_when_no_search_results_throws(self, mock_spotify_client: MagicMock,
                                                     mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.search.return_value = _read_file_as_json(
            f"{self.resources_}/spotipy/input/search.json")
        spotipy_client = SpotipyClient(config_path=self.config)
        try:
            spotipy_client.get_album(Music("no-match-title", "no-match-artist"))
        except MusicNotFoundError:
            pass






