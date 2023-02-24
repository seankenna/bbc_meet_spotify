from unittest.mock import patch, MagicMock, call

from bbc_meet_spotify import Spotify, MusicNotFoundError
from bbc_meet_spotify.music import Music


class TestSpotify:
    @patch("bbc_meet_spotify.spotify.SpotipyClient")
    def test_add_albums_when_no_albums(self, mock_spotipy_client: MagicMock):
        mock_spotipy_client_instance = mock_spotipy_client.return_value
        mock_spotipy_client_instance.get_playlist.return_value = {"id": "1"}
        spotify = Spotify()
        spotify.add_albums("test-playlist-name", [])
        mock_spotipy_client_instance.get_album.assert_not_called()
        mock_spotipy_client_instance.add_music_to_playlist.assert_not_called()
        assert spotify.music_not_found == []

    @patch("bbc_meet_spotify.spotify.SpotipyClient")
    def test_add_albums_when_exception(self, mock_spotipy_client: MagicMock):
        mock_spotipy_client_instance = mock_spotipy_client.return_value
        mock_spotipy_client_instance.get_playlist.return_value = {"id": "1"}
        mock_spotipy_client_instance.get_album.side_effect = MusicNotFoundError()
        spotify = Spotify()
        album1 = Music("artist1", "title1")
        spotify.add_albums("test-playlist-name", [album1])
        mock_spotipy_client_instance.get_album.assert_called_with(album1)
        mock_spotipy_client_instance.add_music_to_playlist.assert_not_called()
        assert spotify.music_not_found == ["artist1: title1"]

    @patch("bbc_meet_spotify.spotify.SpotipyClient")
    def test_add_albums(self, mock_spotipy_client: MagicMock):
        mock_spotipy_client_instance = mock_spotipy_client.return_value
        mock_spotipy_client_instance.get_playlist.return_value = {"id": "1"}
        mock_spotipy_client_instance.get_album.side_effect = [{"id": "1"}, {"id": "2"}]
        mock_spotipy_client_instance.add_music_to_playlist.side_effect = [None, None]
        spotify = Spotify()
        album1 = Music("artist1", "title1")
        album2 = Music("artist2", "title2")
        spotify.add_albums("test-playlist-name", [album1, album2])
        mock_spotipy_client_instance.get_album.assert_has_calls([call(album1), call(album2)])
        assert mock_spotipy_client_instance.add_music_to_playlist.call_count == 2
        assert spotify.music_not_found == []

    @patch("bbc_meet_spotify.spotify.SpotipyClient")
    def test_add_songs(self, mock_spotipy_client: MagicMock):
        mock_spotipy_client_instance = mock_spotipy_client.return_value
        mock_spotipy_client_instance.get_playlist.return_value = {"id": "1"}
        mock_spotipy_client_instance.get_song.side_effect = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        mock_spotipy_client_instance.add_music_to_playlist.side_effect = [None, None]
        spotify = Spotify()
        song1 = Music("artist1", "title1")
        song2 = Music("artist2", "title2")
        song3 = Music("artist3", "title3")
        spotify.add_songs("test-playlist-name", [song1, song2, song3])
        mock_spotipy_client_instance.get_song.assert_has_calls([call(song1), call(song2), call(song3)])
        mock_spotipy_client_instance.add_music_to_playlist.assert_called_with("1", ["1", "2", "3"])
        assert spotify.music_not_found == []

    @patch("bbc_meet_spotify.spotify.SpotipyClient")
    def test_add_songs_sanitizes_input(self, mock_spotipy_client: MagicMock):
        mock_spotipy_client_instance = mock_spotipy_client.return_value
        mock_spotipy_client_instance.get_playlist.return_value = {"id": "1"}
        mock_spotipy_client_instance.get_song.side_effect = [MusicNotFoundError(), "1"]
        spotify = Spotify()
        unsanitized_music = Music("artist'1", " title1 ")
        sanitized_music = Music("artist1", "title1")
        spotify.add_songs("test-playlist-name", [unsanitized_music])
        mock_spotipy_client_instance.get_song.assert_has_calls([call(unsanitized_music), call(sanitized_music)])
        mock_spotipy_client_instance.add_music_to_playlist.assert_called_with("1", ["1"])
        assert spotify.music_not_found == []

    @patch("bbc_meet_spotify.spotify.SpotipyClient")
    def test_add_songs_exception(self, mock_spotipy_client: MagicMock):
        mock_spotipy_client_instance = mock_spotipy_client.return_value
        mock_spotipy_client_instance.get_playlist.return_value = {"id": "1"}
        mock_spotipy_client_instance.get_song.side_effect = [MusicNotFoundError(), MusicNotFoundError()]
        spotify = Spotify()
        song1 = Music("artist1", "title1")
        spotify.add_songs("test-playlist-name", [song1])
        mock_spotipy_client_instance.get_song.assert_called_with(song1)
        mock_spotipy_client_instance.add_music_to_playlist.assert_not_called()
        assert spotify.music_not_found == ["artist1: title1"]
