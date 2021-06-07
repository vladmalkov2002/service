# Если у вас не установлены библиотеки, указынные ниже, то вы можете установить их, введя в терминал следующие 4 команды;
# pip install --upgrade flask
# pip install --upgrade google-api-python-client
# pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2
# pip install --upgrade requests
 
import flask
import os
import os.path
import pickle
import json
 
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
 
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
    flask.session['credentials'] = credentials_to_dict(creds)
    fit = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=creds)
 
    data_sources = fit.users().dataSources().list(userId='me').execute()
    if os.path.isfile('data_sources.json'):
        os.remove('data_sources.json')
    with open('data_sources.json', 'w') as f:
        json.dump(data_sources, f)
 
    heart_data = fit.users().dataSources().datasets().get(
        userId='me', dataSourceId=DATA_SOURCE, datasetId=DATA_SET).execute()
    if os.path.isfile('heart_data.json'):
        os.remove('heart_data.json')
    with open('heart_data.json', 'w') as f:
        json.dump(heart_data, f)
    return flask.jsonify(heart_data)
 
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
