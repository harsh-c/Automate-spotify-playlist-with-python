import json
import os
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl

# from exceptions import ResponseException
from secrets import spotify_user_id, spotify_token

class CreatePlaylist: 
    def __init__(self):
        self.user_id = spotify_user_id
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}
    
    # 1: log into youtube
    def get_youtube_client(self):
        """ Log Into Youtube, Copied from Youtube Data API """
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client
        
    # 2: Grab your liked videos from playlist
    def get_liked_videos(self):
        # Get playlist id from youtube & Create A Dictionary Of Important Song Information
        request = self.youtube_client.playlists().list(
        part="snippet",
        mine=True
        )
        response = request.execute()
        
        for item in response["items"]:
            playlist_name = item["snippet"]["title"]
            if playlist_name == "music":
                playlist_id = item["id"]

        request = self.youtube_client.playlistItems().list(
            part="snippet", 
            maxResults=50,
            playlistId = playlist_id
        )
        response = request.execute()
        print(response)

        # collect each video and get important information
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["snippet"]["resourceId"]["videoId"])

            # song_name = video_title
            # use youtube_dl to collect the song name & artist name
            video = youtube_dl.YoutubeDL({}).extract_info(
                youtube_url, download=False)
            song_name = video["track"]
            artist = video["artist"]

            if song_name is not None:
                # save all important info and skip any missing song and artist
                self.all_song_info[video_title] = {
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,

                    # add the uri, easy to get song to put into playlist
                    "spotify_uri": self.get_spotify_uri(song_name, artist)

                }
    
    # 3: Create a new playlist on spotify
    def create_playlist(self):
        request_body = json.dumps({
            "name":"Youtube Liked Songs",
            "description":"",
            "public":"false"
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)

        response = requests.post(
            query,
            data = request_body, 
            headers={
                "Content-Type":"application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            })
        response_json = response.json()

        # playlist id
        return response_json["id"]
    
    # 4: Search for the song in spotify
    def get_spotify_uri(self, song_name, artist):
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name, 
            artist
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]

        # only use the first song
        uri = songs[0]["uri"]

        return uri
        
    # 5: Add the searched song to the new spotify playlist
    def add_song_to_playlist(self):
        """Add all liked songs into a new Spotify playlist"""
        # populate dictionary with our liked songs
        self.get_liked_videos()

        # collect all of uri
        uris = [info["spotify_uri"]
                for song, info in self.all_song_info.items()]

        # create a new playlist
        playlist_id = self.create_playlist()

        # add all songs into new playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        # check for valid response status
        # if response.status_code != 200:
        #     raise ResponseException(response.status_code)

        response_json = response.json()
        return response_json
        
if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.add_song_to_playlist()