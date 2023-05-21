from flask import Flask, render_template, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import configparser

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
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    return spotify.authorize_redirect(redirect_uri)


@app.route("/authorize")
def authorize():
    token = spotify.authorize_access_token()
    if token:
        session["token"] = token
        return redirect(url_for("playlists"))
    else:
        return "Authorization failed."


@app.route("/playlists")
def playlists():
    if "token" in session:
        resp = spotify.get("me/playlists")
        if resp.ok:
            data = resp.json()
            playlists = data["items"]
            return render_template("playlists.html", playlists=playlists)
        else:
            return "Failed to fetch playlists."
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
