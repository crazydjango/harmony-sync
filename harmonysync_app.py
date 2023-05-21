from flask import Flask, render_template, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
import configparser
import logging

def create_app():
    app = Flask(__name__)

    # Read secrets and configuration values from creds_config.txt
    config = configparser.ConfigParser()
    config.read("creds_config.txt")

    app.secret_key = config.get("secrets", "flask_secret_key")

    oauth = OAuth(app)

    # Spotify configuration
    spotify = oauth.register(
        name="spotify",
        client_id=config.get("secrets", "spotify_client_id"),
        client_secret=config.get("secrets", "spotify_client_secret"),
        access_token_url="https://accounts.spotify.com/api/token",
        access_token_params=None,
        authorize_url="https://accounts.spotify.com/authorize",
        authorize_params=None,
        api_base_url="https://api.spotify.com/v1/",
        client_kwargs={"scope": "user-read-private playlist-read-private"},
        redirect_uri=config.get("redirect_uris", "production")
    )

    # Configure logging
    logging.basicConfig(filename='error.log', level=logging.DEBUG)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login")
    def login():
        return spotify.authorize_redirect(url_for("authorize", _external=True))

    @app.route("/callback")
    def authorize():
        try:
            token = spotify.authorize_access_token()
            if token:
                session["token"] = token
                return redirect(url_for("playlists"))
            else:
                return "Authorization failed."
        except Exception as e:
            logging.exception("Error in authorize callback:")
            return jsonify(error="An internal server error occurred. Please try again later.")

    @app.route("/playlists")
    def playlists():
        try:
            if "token" not in session:
                return redirect(url_for("login"))

            token = session["token"]
            resp = spotify.get("me/playlists", token=token)
            playlists = resp.json()["items"]

            playlist_names = [playlist["name"] for playlist in playlists]

            return render_template("playlists.html", playlists=playlist_names)

        except Exception as e:
            logging.exception("Error in playlists route:")
            return jsonify(error="An internal server error occurred. Please try again later.")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port='5000', debug=True)
