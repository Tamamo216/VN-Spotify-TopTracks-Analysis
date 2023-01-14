import os
import pandas as pd
from pathlib import Path
from spotify_utils import SpotifyAPI, get_tracks_data

client_id = '7027619aeac54b5888cfe2aad91e4e51'
client_secret = '867950432f2143ea8f13551e83618da6'

#Instantiate SpotifyAPI object
spotify = SpotifyAPI(client_id, client_secret)
#Get data of Vietnamese artists through Search API Spotify provides with the seach keyword 'việt nam'
print('Extracting VN artist data through Search...')
data = spotify.search(q = 'việt nam', search_type = 'artist', market = 'VN')
print('Done!')
#Obtain the Spotify artist id from the data returned earlier
print('Obtaining artist id...')
artists_id = spotify.get_artist_id_from_search(data)
print('Done!')
#Get top tracks's information of each artist 
print('Extracting top tracks data by artist...')
tracks_data = get_tracks_data(spotify, artists_id)
print('Done!')
#Load data into dataframe and save it as csv file
tracks_df = pd.DataFrame(tracks_data)
parent = Path(__file__).resolve().parents[2]
tracks_df.to_csv(os.path.join(parent, 'data', 'raw data', 'top_tracks_by_artist.csv'), encoding = 'utf-8', index = False)
print('The data have been saved as <{}> folder'.format('raw data'))

