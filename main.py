from bs4 import BeautifulSoup
import requests
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth


BILLBOARD_ENDPOINT = "https://www.billboard.com/charts/hot-100/"  # 2000-08-12

# Spotify Credentials
Client_ID = "Type Here"
Client_Secret = "Type Here"
Redirect_URI = "https://localhost"

wish_list = []
added_songs_list = []


def get_songs_titles(formatted_date: str) -> list:
    """Web scrapes Billboard website for top 100 songs of aspecific dates and saves their 
    titles and songs in two respective lists

    Args:
        formatted_date (str): date in format YYYY-MM-DD

    Returns:
        top_100_list (list): trivial
        artists_list (list): trivial
    """
    top_100_list = []
    artists_list = []

    webpage = requests.get(url=BILLBOARD_ENDPOINT+formatted_date)
    webpage.raise_for_status()

    soup = BeautifulSoup(webpage.text, "html.parser")

    class_name = "c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-16 u-line-height-125 a-truncate-ellipsis"
    class_selector = class_name.replace(" ", ".")
    top_100_song_titles = soup.select("h3."+class_selector+"#title-of-a-story")

    artists_class_name = "c-label a-no-trucate a-font-primary-s u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330"
    artists_class_selector = artists_class_name.replace(" ", ".")
    artists = soup.select("span."+artists_class_selector)

    for song_title in top_100_song_titles:
        top_100_list += [song_title.string.strip()]

    for artist in artists:
        if artist.string.strip() == "'N Sync":
            artists_list += ["*NSYNC"]
        else:
            artists_list += [artist.string.strip()]

    return top_100_list, artists_list


def search_for_one_song(i, song_title: str, artist: str, year: str, wish_list: list, found_match, added_songs_list: list):
    """Searches in Spotify API for any match with a desired song and add all found results
     to wish_list

    Args:
        i (integer): query number
        song_title (str): trivial
        artist (str): trivial
        year (str): trivial
        wish_list (list): IDs of all the desired songs
        found_match (_type_): number of matched songs in Spotify with the scraped list (we don't
        count duplicates)
        added_songs_list (list): contains the number of found results for each song (-1 means
        unsuccessful query from the API)

    Returns:
        wish_list (list), found_match (_type_), added_songs_list (list): these variables are 
        updated after each loop.
    """
    song = sp.search(q="remaster%20track:"+song_title+"%20artist:" +
                     artist+"%20year:"+year, limit=50, offset=0, type='track')

    songs_list = song["tracks"]["items"]
    if len(songs_list) == 0:
        print("No artist in the next query!")
        song = sp.search(q="remaster%20track:"+song_title +
                         "%20year:"+year, limit=50, offset=0, type='track')
        songs_list = song["tracks"]["items"]

    if len(songs_list) == 0:
        print("No track in the next query!")
        song = sp.search(q="remaster%20track:" + artist +
                         "%20year:"+year, limit=50, offset=0, type='track')
        songs_list = song["tracks"]["items"]

    # # Reformatting variables to search for a match
    # Don't forget to give back spaces to this variable
    song_title = song_title.replace("%20", " ").title()
    if "'S" in song_title:
        print("Replacing ('S) with ('s) in the current song title.")
        song_title = song_title.replace("'S", "'s")

    # Removing words with special characters for strings with more than one word
    # if len(song_title.split()) > 1:
    #     song_name = song_title.split()
    #     [song_name.remove(word)
    #      for word in song_title.split() if not word.isalnum()]
    #     song_title = " ".join(song_name)
    print(song_title)
    # Don't forget to give back spaces to this variable
    artist = artist.replace("%20", " ").title()

    if artist == "*Nsync":
        artist = "*NSYNC"
    if "'S" in artist:
        print("Replacing ('S) with ('s) in the current song title.")
        artist = artist.replace("'S", "'s")

    # Removing words with special characters for strings with more than one word
    # if len(artist.split()) > 1:
    #     artist_name = artist.split()
    #     [artist_name.remove(word)
    #      for word in artist.split() if not word.isalnum()]
    #     artist = " ".join(artist_name)
    print(artist)

    found_songs = len(wish_list)

    if len(songs_list) != 0:
        # Checking if the requested songs exists really in the API response
        for item in songs_list:
            if song_title.lower() in item["name"].lower():
                print("Song is found in results file")
                for singer in item["artists"]:
                    if artist.lower() in singer["name"].lower():
                        print("Artist is also found in results file")
                        song_id = item["id"]
                        wish_list += [song_id]

                        break
        if len(wish_list)-found_songs != 0:
            found_match += 1

        print(f"Found query number: {found_match}/100")
        print(f"Added songs: {len(wish_list)-found_songs}")
        added_songs_list += [len(wish_list)-found_songs]
        return wish_list, found_match, added_songs_list
    else:  # Empty API response (unseccessful query)
        added_songs_list += [-1]
        return wish_list, found_match, added_songs_list


def create_wished_playlist(spotify_Clt: object, user_id: str, formatted_date: str, wish_list: list):
    """Creates a new playlist a fills with the found wished songs

    Args:
        spotify_Clt (object): _description_
        user_id (str): _description_
        formatted_date (str): _description_
        wish_list (list): _description_
    """
    # //// Creating an empty list named according to the entered date

    playlist_name = f"Top 100 Songs {formatted_date}"
    playlist_description = f"Takes 100 top songs back in {formatted_date} according to Billboard website."

    sp.user_playlist_create(user=user_id, name=playlist_name,
                            public=False, description=playlist_description)

    # /// Getting the created plylist id
    playlist = sp.current_user_playlists(limit=10, offset=0)

    playlists = playlist["items"]
    for item in playlists:
        if item["name"] == playlist_name:
            playlist_id = item["id"]
            print(playlist_id)
            break

    # /// Adding all the found scraped songs to the created playlist
    reps_num = len(wish_list)//100
    for i in range(0, reps_num):
        sp.user_playlist_add_tracks(
            user_id, playlist_id, wish_list[i*100:(i+1)*100-1], position=None)

    sp.user_playlist_add_tracks(
        user_id, playlist_id, wish_list[reps_num*100:reps_num*100+len(wish_list) % 100], position=None)

################################################################################################


# //// I will assume that the users type dates in correct format
formatted_date = input(
    "Which year do you want to travel to? Type the date in this format YYYY-MM-DD:")  # 2000-08-12

[top_100_list, artists] = get_songs_titles(formatted_date)

# //// Authenticating with Spotify APi and getting User ID
scope = "playlist-modify-private playlist-read-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=Client_ID, client_secret=Client_Secret, redirect_uri=Redirect_URI, scope=scope))


# //// search the scraped songs in Spotify

found_match = 0

for i in range(0, 100):
    # In the query we need to replace spaces with "%20"
    song_title = top_100_list[i].replace(" ", "%20")
    artist = artists[i].replace(" ", "%20")
    year = formatted_date[0:4]
    print(f"song title for query n° {i}: {song_title}")
    print(f"artist for query n° {i}: {artist}")

    wish_list, found_match, added_songs_list = search_for_one_song(
        i, song_title, artist, year, wish_list, found_match, added_songs_list)
    print()


print(f"len(wish_list)={len(wish_list)}")
print(f"Added songs list: {added_songs_list}")
print(
    f"Number of successful queries:  {len(added_songs_list)-added_songs_list.count(-1)}/{len(added_songs_list)}")
print(
    f"Number of found match from queries:{found_match}/100 ;  {len(added_songs_list)-added_songs_list.count(0)-added_songs_list.count(-1)}/{len(added_songs_list)}")


user = sp.current_user()
user_id = user['id']


create_wished_playlist(sp, user_id, formatted_date, wish_list)
