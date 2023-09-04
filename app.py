from flask import Flask, url_for, session, redirect, render_template, abort
from authlib.integrations.flask_client import OAuth
import os
import json
import requests

app = Flask(__name__)

appConf = {
    "OAUTH2_CLIENT_ID": "24970654811-ej6ha7spdgk5iatp91ghosa7kgthu15m.apps.googleusercontent.com",
    "OAUTH2_CLIENT_SECRET": "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",
    "OAUTH2_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
    "FLASK_SECRET": os.urandom(24),
    "FLASK_PORT": 8080
}

oauth =OAuth(app)

oauth.register("myApp",
    client_id=appConf.get("OAUTH2_CLIENT_ID"),
    client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read"
    },
     server_metadata_url=f'{appConf.get("OAUTH2_META_URL")}'
)

app.secret_key = appConf.get("FLASK_SECRET")

@app.route('/')
def index():
    return render_template("index.html", session=session.get("user"), pretty=json.dumps(session.get("user"), indent=4))

@app.route('/signin-google')
def googleLogin():
    if "user" in session:
        abort(404)
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("googleCallback", _external=True))

@app.route("/auth_confirm")
def googleCallback():
     # fetch access token and id token using authorization code
    token = oauth.myApp.authorize_access_token()

    # google people API - https://developers.google.com/people/api/rest/v1/people/get
    # Google OAuth 2.0 playground - https://developers.google.com/oauthplayground
    # make sure you enable the Google People API in the Google Developers console under "Enabled APIs & services" section

    # fetch user data with access token
    personDataUrl = "https://people.googleapis.com/v1/people/me?personFields=genders,birthdays"
    personData = requests.get(personDataUrl, headers={
        "Authorization": f"Bearer {token['access_token']}"
    }).json()
    token["personData"] = personData
    # set complete user information in the session
    session["user"] = token
    return redirect(url_for('index'))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=appConf.get('FLASK_PORT'), debug=True)