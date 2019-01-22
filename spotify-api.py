# Import libraries
import requests
import json

## Official documentation: https://developer.spotify.com/documentation/web-api/

# Getting setup
"""
We first have to go into https://developer.spotify.com/dashboard/applications
to create a new application.
Once this application is created, we need to generate a Client ID and a secret Client ID.
We also need to add a redirect URI on the application by clicking on edit settings,e.g. https://www.getpostman.com/oauth2/callback
"""

# Save down these 3 items from the developer portal
client_id = <CLIENT_ID>
client_secret = <CLIENT_SECRET>
redirect_url = "https://www.getpostman.com/oauth2/callback"

# Set permission scope, if we want to set multiple scopes we need to put them in one string and seperate them by a space
scope = "user-read-private playlist-modify-private playlist-modify-public"

# Define playlists
# Get the playlist ids from rightclicking on the playlist on Spotify Web Player to get the URL. The last part of the URL is the id
read_playlist_id = <READ_PLAYLIST_SPOTIFY_ID>  # This is the source playlist from which we will take songs and move them to the test playlist
test_playlist_id = <TEST_PLAYLIST_SPOTIFY_ID>  # Test playlist
new_playlist_id = <NEW_PLAYLIST_SPOTIFY_ID>  # New playlist

# Set number of songs to be copied in each execution
numberofsongs = 30

# Now we need to log into our Spotify account and pass captcha, this needs to be done in a browser. Once logged in, the browser will redirect to a new URL that will look like:
# https://app.getpostman.com/oauth2/callback?code=AQAxQFFbbDBvbDsxTsoQhuU3suo1GuDtgdOfh-LMtCufSTpEPx5PDGPVyxI6HlCAoee8Geyr1N6Jsf-jRC8g0Sd0DoiOLBkupzfOXiKllqvb3Ye8e87T8_DZs3p5KhcyooKQdd7kmorF8wzYrhyfEkQKugg47x3vQab1sdrUlLdVMepOZZD-UgeKl4YVQ66VbB3M5saTdzVW_op_hlkgkXT5avvOu_Y365a-rU9-8Qais-2kU8TDxuer5r3McVjAJYa1G5JiniZoes0t
# From this URL we need to copy what comes after "code=" and save it in the authorization_code variable below


def get_authorization_code():
    authparameters = {"client_id": client_id, "response_type": "code", "redirect_uri": redirect_url, "scope": scope}
    authresponse = requests.get("https://accounts.spotify.com/authorize", params=authparameters)
    import webbrowser
    webbrowser.open(authresponse.url)


def save_tokens():
    # Save authorization code here
    authorization_code = <AUTHORIZATION_CODE>

    # Now we retrieve the Access and Refresh Tokens
    tokenbody = {"grant_type": "authorization_code", "code": authorization_code, "redirect_uri": redirect_url, "client_id": client_id, "client_secret": client_secret}
    tokenresponse = requests.post("https://accounts.spotify.com/api/token", data=tokenbody)
    if tokenresponse.status_code == 200:
        print("Access and Refresh tokens retrieved.")
    # Save access and refresh token from response
    tokendict = json.loads(tokenresponse.text)
    access_token = tokendict["access_token"]
    refresh_token = tokendict["refresh_token"]

    # Set the requestheader to be used by all calls
    global requestheader
    requestheader = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}


def refresh_access_token():
    print("Refreshing Token.")
    # Save the refresh token here to skip the previous functions after first use
    refresh_token = <REFRESH_TOKEN>

    # Use the refresh token to get a new access token
    refreshbody = {"grant_type": "refresh_token", "refresh_token": refresh_token, "client_id": client_id, "client_secret": client_secret}
    refreshresponse = requests.post("https://accounts.spotify.com/api/token", data=refreshbody)
    if refreshresponse.status_code == 200:
        print("Token Refreshed.")

    # Save new access_token
    access_token = json.loads(refreshresponse.text)["access_token"]

    # Update requestheader
    global requestheader
    requestheader = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}


def move_to_new():
    # Move songs on the test playlist to the new playlist, then get a new batch of songs to put on the test playlist
    print("Getting tracks to move.")

    # Read all test playlist track ids
    testread_response = requests.get(f"https://api.spotify.com/v1/playlists/{test_playlist_id}/tracks", headers=requestheader)
    testread_responsedict = json.loads(testread_response.text)
    if testread_response.status_code == 200:
        print("Step 1 - Read tracks from test_playlist.")
    try:
        tracklist = [testread_responsedict["items"][x]["track"]["uri"] for x in range(testread_responsedict["total"])]
        # Add to the new playlist
        new_body = {"uris": tracklist}
        new_response = requests.post(f"https://api.spotify.com/v1/playlists/{new_playlist_id}/tracks", headers=requestheader, json=new_body)
        if new_response.status_code == 200:
            print("Step 2 - Moved tracks to new_playlist.")
    except KeyError as key:
        if key == "total":
            print("Step 2 - Playlist uninitialised - Proceeding to adding new songs.")


def read_tracks_to_copy():
    parameters = {"limit": numberofsongs}
    # Get track ids from the source playlist
    read_response = requests.get(f"https://api.spotify.com/v1/playlists/{read_playlist_id}/tracks", headers=requestheader, params=parameters)
    if read_response.status_code == 200:
        print("Step 3 - Read tracks from read_playlist.")
    responsedict = json.loads(read_response.text)
    unfilteredtracklist = [responsedict["items"][x]["track"]["uri"] for x in range(numberofsongs)]
    global tracklist
    tracklist = [track for track in unfilteredtracklist if track[8:13] == "track"]

    # If there are local songs (songs not available online), we need to filter these out as these cannot be moved
    if len(tracklist) < numberofsongs:
        additionaltracks = 0
        offsetposition = numberofsongs
        while len(tracklist) < numberofsongs:
            offsetposition += additionaltracks
            additionaltracks = numberofsongs - len(tracklist)
            parameters = {"limit": additionaltracks, "offset": offsetposition}
            read_response = requests.get(f"https://api.spotify.com/v1/playlists/{read_playlist_id}/tracks", headers=requestheader, params=parameters)
            responsedict = json.loads(read_response.text)
            unfilteredtracklist = [responsedict["items"][x]["track"]["uri"] for x in range(additionaltracks)]
            for track in unfilteredtracklist:
                if track[8:13] == "track":
                    tracklist.append(track)


def replace_test_playlist_songs():
    # Format test_body and replace songs on the test playlist with new batch of songs
    test_body = {"uris": tracklist}
    test_response = requests.put(f"https://api.spotify.com/v1/playlists/{test_playlist_id}/tracks", headers=requestheader, json=test_body)
    if test_response.status_code == 201:
        print("Step 4 - Replace tracks on test_playlist.")


def delete_from_read_playlist():
    # Delete same batch of songs from the source playlist
    dellist = []
    for track in tracklist:
        dellist.append({"uri": track})
    del_body = {"tracks": dellist}

    del_response = requests.delete(f"https://api.spotify.com/v1/playlists/{read_playlist_id}/tracks", headers=requestheader, json=del_body)
    if del_response.status_code == 200:
        print("Step 5 - Delete tracks on read_playlist.")


def main():
    refresh_access_token()
    move_to_new()
    read_tracks_to_copy()
    replace_test_playlist_songs()
    delete_from_read_playlist()
    print("Successful - Exiting.")


if __name__ == "__main__":
    main()
