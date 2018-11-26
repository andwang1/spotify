# Spotify Web API

--- SPOTIFY AUTHORIZATION STEPS ---

This program will lead the user through the Spotify API Authorization Code Flow as outlined on https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow.

These steps are only required on first usage of this program. Once the refresh token is retrieved for the first time and all other static attributes are saved in the script where prompted, the token can be used to regenerate new access tokens.

In terms of the program, this means that while all of the functions need to be called on the first usage, afterwards the user can skip to  refresh_access_token().

--- USAGE ---

The program uses 3 playlists: A "test" playlist, a "new" playlist and an "old" playlist.
The purpose of this program is to take a number of songs from the old playlist and move it to the test playlist, after all of the songs on the test playlist were moved over to the new playlist.
I use this program to clean a very large old playlist that I have. I move 30 songs from this playlist to a test playlist. This test playlist I will then listen to while travelling or working. Any songs I do not want to keep, I delete while listening from the playlist. Once I have listened to all the songs, I execute the program - all remaining songs on the test playlist are moved to my new cleaned playlist and a new batch of test songs are moved to the test playlist.
