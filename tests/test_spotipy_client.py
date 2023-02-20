import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from bbc_meet_spotify import MusicNotFoundError
from bbc_meet_spotify.music import Music
from bbc_meet_spotify.spotipy_client import SpotipyClient


class TestSpotipyClient:
    def setup(self):
        test_resources = Path(__file__).parent / "resources"
        self.config = test_resources / "config.toml"

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_add_music_to_playlist_when_no_new_song_ids_then_returns(self, mock_spotify_client: MagicMock,
                                                                     mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.user_playlist.return_value = {"tracks": {"items": [{"track": {"id": 1}},
                                                                                        {"track": {"id": 2}},
                                                                                        {"track": {"id": 3}}]}}
        spotipy_client = SpotipyClient(config_path=self.config)
        spotipy_client.add_music_to_playlist("test-playlist-id", [1, 2, 3])
        mock_spotify_client_instance.user_playlist_add_tracks.assert_not_called()

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_add_music_to_playlist_when_new_song_ids_then_adds_tracks(self, mock_spotify_client: MagicMock,
                                                                      mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.user_playlist.return_value = {"tracks": {"items": []}}
        spotipy_client = SpotipyClient(config_path=self.config)
        spotipy_client.add_music_to_playlist("test-playlist-id", [1, 2, 3])
        mock_spotify_client_instance.user_playlist_add_tracks.assert_called_with("bbc_meet_spotify",
                                                                                 "test-playlist-id", [1, 2, 3])

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    @patch("bbc_meet_spotify.spotipy_client.time.strftime", return_value="2013-02-01")
    def test_create_playlist_when_playlist_exists_then_returns_existing_playlistid(self, mock_time: time,
                                                                                   mock_spotify_client: MagicMock,
                                                                                   mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.user_playlists.return_value = {"items": [{"name": "2013-02-01_test-playlist-id",
                                                                               "id": 1}]}
        spotipy_client = SpotipyClient(config_path=self.config)
        playlist_id = spotipy_client.create_playlist("test-playlist-id")
        mock_spotify_client_instance.user_playlists.is_called_with("2013-02-01_test-playlist-id")
        mock_spotify_client_instance.user_playlist_create.assert_not_called()
        assert playlist_id == 1

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_create_playlist_when_playlist_new_then_returns_new_playlistid(self, mock_spotify_client: MagicMock,
                                                                           mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.user_playlists.return_value = {"items": []}
        mock_spotify_client_instance.user_playlist_create.return_value = {"id": 2}
        spotipy_client = SpotipyClient(config_path=self.config)
        playlist_id = spotipy_client.create_playlist("test-playlist-id", False)
        mock_spotify_client_instance.user_playlist_create.assert_called_with("bbc_meet_spotify", "test-playlist-id",
                                                                             public=True)
        assert playlist_id == 2

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_create_playlist_when_playlist_new_then_returns_new_private_playlistid(self, mock_spotify_client: MagicMock,
                                                                                   mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.user_playlists.return_value = {"items": []}
        mock_spotify_client_instance.user_playlist_create.return_value = {"id": 2}
        spotipy_client = SpotipyClient(config_path=self.config)
        playlist_id = spotipy_client.create_playlist("test-playlist-id", False, False)
        mock_spotify_client_instance.user_playlist_create.assert_called_with("bbc_meet_spotify", "test-playlist-id",
                                                                             public=False)
        assert playlist_id == 2

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_query_spotify_track(self, mock_spotify_client: MagicMock, mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.search.side_effect = [{"tracks": {"items": [{"name": "title", "id": 1},
                                                                                 {"name": "title", "id": 2},
                                                                                 {"name": "no-match", "id": 3}
                                                                                 ]}}]
        spotipy_client = SpotipyClient(config_path=self.config)
        track_id = spotipy_client.query_spotify_track(Music("artist", "title"))
        mock_spotify_client_instance.search.assert_called_with(q="artist:artist track:title")
        assert track_id == 1

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_query_spotify_track_when_no_search_results_throws(self, mock_spotify_client: MagicMock,
                                                               mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.search.return_value = []
        spotipy_client = SpotipyClient(config_path=self.config)
        try:
            spotipy_client.query_spotify_track(Music("artist", "title"))
        except MusicNotFoundError:
            pass

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_query_spotify_track_when_no_match_results_throws(self, mock_spotify_client: MagicMock,
                                                              mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.search.side_effect = [{"tracks": {"items": [{"name": "not-me", "id": 1}]}}]
        spotipy_client = SpotipyClient(config_path=self.config)
        try:
            spotipy_client.query_spotify_track(Music("artist", "title"))
        except MusicNotFoundError:
            pass

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_query_spotify_album_tracks(self, mock_spotify_client: MagicMock, mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.search.side_effect = [{"tracks": {"items": [{"id": 1}, {"id": 2}, {"id": 3}]}}]
        spotipy_client = SpotipyClient(config_path=self.config)
        tracks = spotipy_client.query_spotify_album_tracks(Music("title", "artist"))
        mock_spotify_client_instance.search.assert_called_with(q="artist:title album:artist")
        assert tracks == [1, 2, 3]

    @patch("bbc_meet_spotify.spotipy_client.spotipy.util.prompt_for_user_token", return_value="test-token")
    @patch("bbc_meet_spotify.spotipy_client.spotipy.Spotify")
    def test_query_spotify_album_tracks_when_no_search_results_throws(self, mock_spotify_client: MagicMock,
                                                                      mock_get_spotify_token: MagicMock):
        mock_spotify_client_instance = mock_spotify_client.return_value
        mock_spotify_client_instance.search.return_value = []
        spotipy_client = SpotipyClient(config_path=self.config)
        try:
            spotipy_client.query_spotify_album_tracks(Music("title", "artist"))
        except MusicNotFoundError:
            pass
