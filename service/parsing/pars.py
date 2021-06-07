# pip install --upgrade flask
# pip install --upgrade google-api-python-client
# pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2
# pip install --upgrade requests

import flask
import os.path
import pickle
import json
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

import google_auth_oauthlib.flow
import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from flask import redirect

import time
from datetime import datetime

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/fitness.heart_rate.read']
API_SERVICE_NAME = 'fitness'
API_VERSION = 'v1'

DATA_SOURCE = 'derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm'
NOW = datetime.today()
START = 0
END = int(time.mktime(NOW.timetuple())*1000000000)
DATA_SET = "%s-%s" % (START, END)

app = flask.Flask(__name__)
app.secret_key = 'odinopokum'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://u_ecg:2021_ECG@92.242.58.173:1984/db_ecg'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class data6(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bpm = db.Column(db.Integer, primary_key=False)
    time = db.Column(db.BigInteger, primary_key=False)
    datasource = db.Column(db.String(150), primary_key=False)
    def __init__(self, bpm, time, datasource):
        self.bpm = bpm
        self.time = time
        self.datasource = datasource

db.create_all()

# me = data2(12)
# db.session.add(me)
# db.session.commit()

@app.route('/')
def index():
    return print_index_table()


@app.route('/test')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_console()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    fit = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=creds)

    data_sources = fit.users().dataSources().list(userId='me').execute()
    with open('data_sources.json', 'w') as f:
        json.dump(data_sources, f)
    heart_data = fit.users().dataSources().datasets().get(
        userId='me', dataSourceId=DATA_SOURCE, datasetId=DATA_SET).execute()
    with open('heart_data.json', 'w') as f:
        json.dump(heart_data, f)
    flask.session['credentials'] = credentials_to_dict(creds)
    parse_heart_data()
    return redirect("http://127.0.0.1:5000/data_base") # json.dumps(heart_list, indent=4) # flask.jsonify(heart_data)

def parse_heart_data():
    f = open('heart_data.json',)
    heart_data = json.load(f)
    for ind in range(len(heart_data["point"])):
        heart_point = {}
        ms = heart_data["point"][ind]["modifiedTimeMillis"]
        heart_point["time"] = datetime.fromtimestamp(float(ms) // 1000.0)
        heart_point["bpm"] = heart_data["point"][ind]["value"][0]["fpVal"]
        source = heart_data["point"][ind]["originDataSourceId"].split(':')
        heart_point["data source"] = source[2]
        if heart_point["data source"] != "com.google.android.gms":
            heart_point["manufacturer"] = source[3]
            heart_point["device type"] = source[4]
            heart_point["uid"] = source[5]
        fav=data6(bpm=heart_point.get('bpm'), time = (heart_point.get('time')), datasource = heart_point.get('data source'))
        db.session.add(fav)
        db.session.commit()
    f.close()
    return

@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',include_granted_scopes='true')

    flask.session['state'] = state
    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    SCOPES = None
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('test_api_request'))

@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Get heart rate data</a></td></tr>' +
          '<tr><td><a href="/clear">Clear credentials</a></td></tr>')

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8080, debug=True)
