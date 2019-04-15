import os
import boto3
import requests
import json

# General
s3 = boto3.resource('s3')
lambdaClient = boto3.client('lambda')


def songBotCronCall(event, context):

    songList = []
    class Song:
        def __init__(self, id, title, url):
            self.id = id
            self.title = title
            self.url = url

    # SoundCloud
    soundcloudUserId = 'users/580297311/playlists'
    soundcloudClientId = '?client_id=xIa292zocJP1G1huxplgJKVnK0V3Ni9D'
    soundcloudApiEndpoint = 'http://api.soundcloud.com/'

    soundCloudDownloadAllPlaylist = True
    playlistToDownload = []

    if soundCloudDownloadAllPlaylist:
        #get all playlist and then tracks
        requestResponse = requests.get(soundcloudApiEndpoint + soundcloudUserId + soundcloudClientId)
        #requestResponse = requests.get('http://api.soundcloud.com/users/580297311/playlists?client_id=xIa292zocJP1G1huxplgJKVnK0V3Ni9D')
        jsonResponse = requestResponse.json()

        for playlist in jsonResponse:
            for track in playlist['tracks']:
                songList.append(Song(None, track['title'], track['permalink_url']))
                
    else:
        if playlistToDownload:
            for playlistId in playlistToDownload:
                requestResponse = requests.get(soundcloudApiEndpoint + playlistId + 'playlists' + soundcloudClientId)
                #requestResponse = requests.get('http://api.soundcloud.com/playlists?client_id=xIa292zocJP1G1huxplgJKVnK0V3Ni9D')
                jsonResponse = requestResponse.json()

        else:
            print('no playlist to download.')


    #  YouTube
    key = os.environ['key']
    youtubeChannelId = os.environ['youtubeChannelId']
    youtubeApiEndpoint = 'https://www.googleapis.com/youtube/v3/'

    youtubeDonwloadAllPlaylist = False
    playlistToDownload = ['PL79EnF5Uf84FJ__-mhSEpWgKSUXX0cv-P']

    if youtubeDonwloadAllPlaylist:
        pass
    else:
        if playlistToDownload:
            for playlistId in playlistToDownload:
                payload = {'part':'snippet', 'maxResults':'50', 'playlistId':playlistId, 'key':key}
                requestResponse = requests.get(youtubeApiEndpoint + 'playlistItems', params=payload)
                jsonResponse = requestResponse.json()

                for song in jsonResponse['items']:
                    youtubeSongId = song['snippet']['resourceId']['videoId']
                    youtubeSongTitle = song['snippet']['title']
                    songList.append(Song(youtubeSongId, youtubeSongTitle, None))

        else:
            print('No playlist to download')


    # Check s3 for repeats
    s3bucket = s3.Bucket(name='yt-mp3-storage')

    bucketList = []

    for item in s3bucket.objects.all():
        bucketList.append(item.key[:-4])

    for song in songList:
        if song.title not in bucketList:
            lambdaPayload = {'songID': song.id, 'songTitle': song.title, 'songUrl': song.url}
            invoke = lambdaClient.invoke(
                FunctionName='youtube-download-bot-dev-download',
                InvocationType='Event',
                Payload=json.dumps(payload)
            )
            print(invoke)


            
