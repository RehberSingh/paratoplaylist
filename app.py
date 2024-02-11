"""
Prerequisites

    pip3 install spotipy Flask Flask-Session

    // from your [app settings](https://developer.spotify.com/dashboard/applications)
    export SPOTIPY_CLIENT_ID=4f4ace57c5624d0d8a5d2d7bd5a30747
    export SPOTIPY_CLIENT_SECRET=5ac5d16e36a640c29c026aff903b221a
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080' // must contain a port
    // SPOTIPY_REDIRECT_URI must be added to your [app settings](https://developer.spotify.com/dashboard/applications)
    OPTIONAL
    // in development environment for debug output
    export FLASK_ENV=development
    // so that you can invoke the app outside of the file's directory include
    export FLASK_APP=/path/to/spotipy/examples/app.py

    // on Windows, use `SET` instead of `export`

Run app.py

    python3 app.py OR python3 -m flask run
    NOTE: If receiving "port already in use" error, try other ports: 5000, 8090, 8888, etc...
        (will need to be updated in your Spotify app and SPOTIPY_REDIRECT_URI variable)
"""

import os
from flask import Flask, session, request, redirect, render_template
from flask_session import Session
import spotipy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)


@app.route('/')
def index():

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
                                               cache_handler=cache_handler,
                                               show_dialog=True)

    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 3. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return render_template('index.html')



@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/')


@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()

@app.route('/search', methods=['POST'])
def search():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    search_query = request.form['q']
    print(search_query)
    #return spotify.search(search_query, limit=10, offset=0, type='track')
    return str(search_query)

@app.route('/test', methods=['POST'])
def test():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    def search_spotify(q):
        word_list = q.split()
        l = []
        for word in word_list:
            offset = 0
            found_song = False  # Flag to track if song is found
            while True:
                # Search for tracks
                track_results = spotify.search(word, limit=50, offset=offset, type='track')
                # Check if any tracks were found
                if not track_results['tracks']['items']:
                    break  # No more tracks found for this word, exit the loop

                tracks = track_results['tracks']['items']
                for track in tracks:
                    if track['name'].lower() == word.lower():
                        l.append(track)
                        found_song = True  # Set flag to True if song is found
                        break  # Exit the loop if song is found

                if found_song:
                    break  # Exit the while loop if song is found

                # Move to the next page of results
                if track_results['tracks']['next']:
                    offset += 50  # Move the offset to the next page
                else:
                    break  # No more pages, exit the loop

        return l
    q = request.form['q']
    print(q)
    return render_template('tracks.html', tracks=search_spotify(q))


        

