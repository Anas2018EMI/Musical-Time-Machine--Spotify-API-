# Musical-Time-Machine--Spotify-API-

This script creates top 100 songs of any date you specify in the prompt. Before running the script you need to sign up for a Spotify developer
account, create an app and paste your Client ID and Client Secret in the script variables.
When you first time launch the script, a blank webpage routed to localhost will appear. You need to paste the URL of that webpage in the
terminal. Then you will be authenticated to Spotify API.

The script works as the following: it web scrapes a Billboard webpage of top 100 songs of the given date. Then, it uses Spotify API to create
a new playlist and fills it with matching songs found in Billboard website.
