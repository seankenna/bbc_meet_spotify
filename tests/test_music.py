from bbc_meet_spotify.music import Music


def test_clean_string():
    music = Music("artist&$£ ft.", "title feat.")
    assert music.title == "title"
    assert music.artist == "artist"


def test_get_sanitised_music():
    music = Music(" art'.ist ", " tit'.le ")
    music = music.sanitize()
    assert music.title == "title"
    assert music.artist == "artist"


def test_to_string():
    music = Music("artist", "title")
    music = music.to_string()
    assert music == "artist: title"
