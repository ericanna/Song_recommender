#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import config
import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials
from IPython.display import IFrame, display
import random

hot_100 = pd.read_csv("hot_100.csv")

hot_100.drop(columns = ['Unnamed: 0'], inplace = True)
print(hot_100)

song_random = hot_100.sample()

songs = []
for i in hot_100['Song']:
    songs.append(i)
    
artists = []
for i in hot_100['Artist']:
    artists.append(i)

def treating_typos_song():
    song_input = input("Please, write the title of the song.")
    if process.extractOne(song_input, songs)[1] > 80:
        song_ = process.extractOne(song_input, songs)[0]
    else:
        song_ = song_input
    return song_

def treating_typos_artist():
    artist_input = input("Please, write the name of the artist.")
    if process.extractOne(artist_input, artists)[1] > 80:
        artist_ = process.extractOne(artist_input, artists)[0]
    else:
        artist_ = artist_input
    return artist_

def filter_song_out(song, artist):
    idx = hot_100.index[(hot_100['Song'] == song) & (hot_100['Artist'] == artist)].tolist()[0]
    hot_100.drop(idx)

spotify_songs = pd.read_csv("songs2.csv")
spotify_songs

X = spotify_songs.drop(columns = spotify_songs[["id", "Unnamed: 0.1", "Unnamed: 0"]]) #removing the if column so it doesn't get standardized

scaler = StandardScaler()
scaler.fit(X)
X_scaled = scaler.transform(X)
X_scaled_df = pd.DataFrame(X_scaled, columns = X.columns)

kmeans = KMeans(n_clusters=300, random_state=1234)
kmeans.fit(X_scaled_df)

clusters = kmeans.predict(X_scaled_df)
pd.Series(clusters).value_counts().sort_index()

X["cluster"] = clusters

spotify_df = pd.concat([X, spotify_songs["id"]], axis=1)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= config.client_id,
                                                           client_secret= config.client_secret))

def hot_songs():
    song_ = treating_typos_song()
    artist_ = treating_typos_artist()
    
    if song_ in songs and artist_ in artists:
        filter_song_out(song_, artist_)
        x = list(song_random["Song"])[0]
        y = list(song_random["Artist"])[0]
        output_song1 = sp.search(q=y + x, limit=1)
        track_id1=output_song1["tracks"]["items"][0]["id"]
        music1 = IFrame(src="https://open.spotify.com/embed/track/"+track_id1,
                      width="320",
                      height="80",
                     frameborder="0",
                      allowtransparency="true",
                      allow="encrypted-media",
                    )
        print("Your song is in the top 100 and this is our recommendation for you:")
        display(music1)
    else:
        input_song = sp.search(q=artist_ + song_,limit=1)
        track_id=input_song["tracks"]["items"][0]["id"]
        music = IFrame(src="https://open.spotify.com/embed/track/"+track_id,
                      width="320",
                      height="80",
                     frameborder="0",
                      allowtransparency="true",
                      allow="encrypted-media",
                    )
        
        
        display(music)
        confirmation = input("Is this the song you chose?(y/n) ")
        print(confirmation)
        if confirmation == "n":
            print("Please, try again.")
        elif confirmation == "y":
            song_df = pd.DataFrame(sp.audio_features(input_song["tracks"]["items"][0]["id"]))
            song_df=song_df[["danceability","energy","loudness","speechiness","acousticness", "instrumentalness","liveness","valence","tempo","id","duration_ms"]]
            song_df2 = song_df.drop(columns = "id")
            song_df2_scaled = scaler.transform(song_df2)
            song_df2_scaled = pd.DataFrame(song_df2_scaled, columns = song_df2.columns)
            cluster = int(kmeans.predict(song_df2_scaled))
            similar_songs = list(np.where(spotify_df["cluster"] == cluster)[0])
            recommendation = random.choice(similar_songs)
            id_recommendation = spotify_df.iloc[recommendation,11]
            output_song = IFrame(src="https://open.spotify.com/embed/track/"+id_recommendation,
                             width="320",
                             height="80",
                             frameborder="0",
                             allowtransparency="true",
                             allow="encrypted-media",
                            )
            print("This is our recommendation for you:")
            return output_song
        else:
            print("You should type y for yes or n for no. Please try again.")

hot_songs()