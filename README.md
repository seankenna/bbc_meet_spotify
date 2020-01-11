# bbc_meet_spotify
Simple tool to convert BBC radio station playlists into spotify playists

## Why

BBC used to be friendly for spotify users and create spotify playlists of their A, B and C-list songs for that week.
It looks like when they moved everything to BBC Sounds, that they wanted to make people use it, so stopped putting
their playlists on Spotify. This is a low effort way to get those playlists back on spotify.

### Other options that didn't work for me:

- [rdfaudio](https://github.com/hubgit/rdfaudio)  (Javascripy chrome plugin) never populated a playlist for me.
- [spotify_bb6](https://github.com/louridas/spotify_bbc6/blob/master/spotify_bbc6.py) (python) relied on spotify 
  links existing on the bbc page, the weekly playlist doesn't have this anymore so additional work 
  scraping the track info and then searching spotify was needed
- [beebify](https://github.com/adamobeng/beebify) (python) scraped the information from a different format
  of bbc playlist which didn't work for the weekly playlists sadly.
- [bbcr1-spotify](https://github.com/denysvitali/bbcr1-spotify) (Crystal) seemed like it would only populate playlist 
  with bbc radio 1 now playing
  
## Installation & setup

1. Clone repository 

    ```bash
    git clone https://github.com/stefpiatek/bbc_meet_spotify.git
    ```

2. With **Python 3.6 or higher**, set up virtual environment
    
    ```bash
    cd bbc_meet_spotify
    # Create the virtual environment
    python3.6 -m venv .venv 
    # Enable the virtual environment
    source .venv/bin/activate
    ```

3. Install requirements

    ```bash
    pip install -r requirements.txt
    ```

4. Follow the instructions for [authorisation of spotify apps](https://spotipy.readthedocs.io/en/latest/#authorized-requests)
   (which involves [registering your app](https://developer.spotify.com/dashboard/)). 
   The name of the application can be whatever you'd like. 

5. Copy the `config_example.toml` to a new file `config.toml`.
   - Fill in the config `client_id` and `client_secret` from the application you registered with spotify.
   - Fill in your spotify `username` field.


## Usage

The simplest usage is to use the default values `python bbc_meet_spotify.com`

- This will get all songs from the BBC 6 Music playlist page
- Create a public playlist prefixed with today's date, e.g. `2020-01-11_BBC 6 Music`.
  If a playlist by this name already exists, it will just use this playlist.
- Add all songs that it can find on spotify to the playlist if they aren't already in the playlist.
    - If any songs can't be found, the song will be logged and you can add these manually.

`2020-01-11 21:51:06.133 | ERROR    | __main__:_get_song_id:193 - Could not find a song: <Juniore: Ah Bah D Accord>`
    

### Command line options

Command line options are generated by [click](https://click.palletsprojects.com), 
see their documentation if you need help using the command line options.  


You can view the command line options by `python bbc_meet_spotify.py --help`

```text
Usage: bbc_meet_spotify.py [OPTIONS]

Options:
  -k, --playlist-key [6music|radio1]
                                  Playlist key to use from
                                  `bbc_playlists.toml`
  -d, --date-prefix BOOLEAN       Do you want to add a date prefix to be added
                                  to your spotify playlist?
  -p, --public-playlist BOOLEAN   Do you want to make your playlist public?
  -n, --custom-playlist-name TEXT
                                  Use this if you don't want the default
                                  playlist name for the radio
  --help                          Show this message and exit.

```

The default command line options are equivalent to calling: 

```bash
python bbc_meet_spotify.py --playlist-key 6music --date-prefix true --public-playlist true
```

