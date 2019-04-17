import os
import boto3
import requests
import json

# General
s3 = boto3.resource('s3')
lambdaClient = boto3.client('lambda')


def songbotCronCall(event, context):

    songList = []
    class Song:
        def __init__(self, service, title, url):
            self.service = service
            self.title = title
            self.url = url

    #################### soundcloud ####################
    # SoundCloud fixed variables
    soundcloudUserId = 'users/580297311/playlists'
    soundcloudApiEndpoint = 'http://api.soundcloud.com/'

    # SoundCloud env variables loaded
    soundcloudClientId = '?client_id=' + os.environ['soundcloudClientId']
    soundcloudDownloadAllPlaylist = os.environ['soundcloudDownloadAllPlaylist']
    soundcloudPlaylistToDownload = os.environ['soundcloudPlaylistToDownload']

    #get all playlist and then tracks
    if soundcloudDownloadAllPlaylist == 'True':
        requestResponse = requests.get(soundcloudApiEndpoint + soundcloudUserId + soundcloudClientId)
        jsonResponse = requestResponse.json()
        for playlist in jsonResponse:
            for track in playlist['tracks']:
                songList.append(Song('soundcloud', track['title'], track['permalink_url']))              
    else:
        if soundcloudPlaylistToDownload:
            playlistIds = soundcloudPlaylistToDownload.split('|')
            for playlistId in playlistIds:
                requestResponse = requests.get(soundcloudApiEndpoint + playlistId + 'playlists' + soundcloudClientId)
                jsonResponse = requestResponse.json()
        else:
            print('no playlist to download.')


    ####################  YouTube ####################
    # youTube fixed variables
    youtubeApiEndpoint = 'https://www.googleapis.com/youtube/v3/'

    # youTube env variables loaded
    youtubeChannelId = os.environ['youtubeChannelId']
    youtubeApiKey = os.environ['youtubeApiKey']
    youtubeDonwloadAllPlaylist = os.environ['youtubeDonwloadAllPlaylist']
    youtubePlaylistToDownload = os.environ['youtubePlaylistToDownload']

    if youtubeDonwloadAllPlaylist == 'True':
        pass       
    else:
        if youtubePlaylistToDownload:
            playlistIds = youtubePlaylistToDownload.split('|')
            for playlistId in playlistIds:
                payload = {'part':'snippet', 'maxResults':'50', 'playlistId':playlistId, 'key':youtubeApiKey}
                requestResponse = requests.get(youtubeApiEndpoint + 'playlistItems', params=payload)
                jsonResponse = requestResponse.json()
                for song in jsonResponse['items']:
                    youtubeSongId = song['snippet']['resourceId']['videoId']
                    youtubeSongTitle = song['snippet']['title']
                    songList.append(Song('youtube', youtubeSongTitle, 'https://www.youtube.com/watch?v=' + youtubeSongId))
        else:
            print('No playlist to download')


    # Check s3 for repeats
    s3bucket = s3.Bucket(name=os.environ['s3bucket'])
    bucketList = []

    for item in s3bucket.objects.all():
        bucketList.append(item.key[:-4])
    for song in songList:
        if song.title not in bucketList:
            lambdaPayload = {'service': song.service, 'songTitle': song.title, 'songUrl': song.url}
            invoke = lambdaClient.invoke(
                FunctionName=os.environ['downloadLambdafunction'],
                InvocationType='Event',
                Payload=json.dumps(lambdaPayload)
            )
            print(invoke)


        
