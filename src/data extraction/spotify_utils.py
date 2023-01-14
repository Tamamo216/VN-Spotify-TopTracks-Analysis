import requests
import base64
from urllib.parse import urlencode
import datetime

class SpotifyAPI:
  def __init__(self, client_id, client_secret):
    self.client_id = client_id
    self.client_secret = client_secret
    self.access_token = ''
    self.token_expired_time = datetime.datetime.now()

  def __get_access_token(self):
    '''
    Request Spotify API to give an access token which is required to use other API later.
    Input: None (but you have to specify client_id and client_secret when initiating SpotfyAPI in the beginning)
    Output: an access token which is expired in a limited time
    '''
    client_creds = base64.b64encode('{}:{}'.format(self.client_id,self.client_secret).encode())
    token_request_url = 'https://accounts.spotify.com/api/token'
    token_type = {
      'grant_type' : 'client_credentials'
    }
    token_headers = {
      'Authorization' : 'Basic {}'.format(client_creds.decode())
    }
    token_resp = requests.post(token_request_url, data = token_type, headers = token_headers)
    token_data = token_resp.json()
    self.access_token = token_data['access_token']
    now = datetime.datetime.now()
    self.token_expired_time = now + datetime.timedelta(seconds = token_data['expires_in'])
    return self.access_token

  def __check_token_expired(self):
    '''
    Check if the access token is expired or not
    '''
    now = datetime.datetime.now()
    if now > self.token_expired_time:
      return False
    return True
  
  def search(self, q, search_type, market = None, limit = 50):
    '''
    Return a list of search result based on keyword in query through Spotify API
    Input:
      q: query
      search_type: item types to search across (album, artist, playlist, track)
      market: the country code
      limit: the maximum number of results to return
    Output: list of returned items
    '''
    # Get a new refreshed token if the current token is expired or empty
    if self.access_token == '' or self.__check_token_expired():
      self.access_token = self.__get_access_token()
    endpoint = 'https://api.spotify.com/v1/search'
    headers = {
      'Authorization' : 'Bearer {}'.format(self.access_token),
      'Content-Type' : 'application/json'
    }
    params = ''
    if market != None:
      params = urlencode({'q' : q, 'type' : search_type, 'market' : market, 'limit' : limit})
    else:
      params = urlencode({'q' : q, 'type' : search_type, 'limit' : limit})
    resp = requests.get(endpoint + '?' + params, headers = headers)
    data = resp.json()
    return data

  def get_artist_id_from_search(self, data):
    '''
    Get a list of artists id from search result
    Input: search result
    Output: list of artists id
    '''
    # Get a new refreshed token if the current token is expired or empty
    if self.access_token == '' or self.__check_token_expired():
      self.access_token = self.__get_access_token()
    headers = {
      'Authorization' : 'Bearer {}'.format(self.access_token),
      'Content-Type' : 'application/json'
    }

    artists_id = []
    while data['artists']['next']:
      for artist in data['artists']['items']:
        artists_id.append(artist['id'])
      url = data['artists']['next']
      resp = requests.get(url, headers = headers)
      if resp.status_code == 429:
        raise Exception('API rate limit')
      # Due to a small bug in Spotify API which returns incorrect count of total returned items,
      # the maximum offset that is set to request to API might be larger than the actual count of items,
      # which makes API give the response status code '400'. We will return the result immediately if we
      # encounter this case.
      elif resp.status_code == 400:
        return artists_id
      data = resp.json()
    return artists_id
  
  def artist(self, artist_id):
    '''
    Get artist information through artist id by calling Spotify API
    Input: artist id
    Output: artist information returned from API
    '''
    # Get a new refreshed token if the current token is expired or empty
    if self.access_token == '' or self.__check_token_expired():
      self.access_token = self.__get_access_token()
    headers = {
      'Authorization' : 'Bearer {}'.format(self.access_token),
      'Content-Type' : 'application/json'
    }
    endpoint = 'https://api.spotify.com/v1/artists/{}'.format(artist_id)
    resp = requests.get(endpoint, headers = headers)
    if resp.status_code == 429:
      raise Exception('API rate limit')
    data = resp.json()
    return data

  def artist_top_track(self, artist_id, market):
    '''
    Return a list of top tracks of a specific artist in certain country through Spotify API
    Input: artist id, market
    Output: list of top tracks
    '''
    # Get a new refreshed token if the current token is expired or empty
    if self.access_token == '' or self.__check_token_expired():
      self.access_token = self.__get_access_token()
    headers = {
      'Authorization' : 'Bearer {}'.format(self.access_token),
      'Content-Type' : 'application/json'
    }

    endpoint = 'https://api.spotify.com/v1/artists/{}/top-tracks?market={}'.format(artist_id,market)
    resp = requests.get(endpoint, headers = headers)
    if resp.status_code == 429:
      raise Exception('API rate limit')
    data = resp.json()
    return data['tracks']

def get_tracks_data(spotify, artists_id):
  tracks_data = []
  for artist in artists_id:
    tracks = spotify.artist_top_track(artist, market = 'VN')
    # Retrieve artist info
    artist_data = spotify.artist(artist)
    if artist_data == 429:
      print('API rate limit')
      return tracks_data
    artist_name = artist_data['name']
    artist_followers = artist_data['followers']['total']
    artist_genres = artist_data['genres']

    for track in tracks:
      track_data = {
        'id' : track['id'],
        'name' : track['name'],
        'artist' : artist_name,
        'artist_followers' : artist_followers,
        'artist_genres' : artist_genres,
        'album' : track['album']['name'],
        'release_date' : track['album']['release_date'],
        'album_total_tracks' : track['album']['total_tracks'],
        'duration' : track['duration_ms'],
        'explicit' : track['explicit'],
        'popularity' : track['popularity']
      }
      tracks_data.append(track_data)
  return tracks_data