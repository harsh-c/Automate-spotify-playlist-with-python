# Automate-spotify-playlist-with-python
A simple script that takes your saved videos from your choice of Youtube playlist, and generates a Spotify playlist 

# LocalSetup
Install All Dependencies
pip3 install -r requirements.txt

Collect You Spotify User ID from account overview and Oauth Token From Spotfiy (https://developer.spotify.com/console/post-playlists/) and add it to secrets.py file

Enable Oauth For Youtube and download the client_secrets.json
Ok this part is tricky but its worth it! Just follow the guide here to set up the Youtube Oauth (https://developers.google.com/youtube/v3/getting-started/) 

Next run the File: python3 create_playlist.py

You'll see a long url to authorize the application, click on it and log into your google account to get the authorization code
