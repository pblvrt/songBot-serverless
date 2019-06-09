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
    if soundcloudDownloadAllPlaylist == 'Yes':
        requestResponse = requests.get(soundcloudApiEndpoint + soundcloudUserId + soundcloudClientId)
        jsonResponse = requestResponse.json()
        for playlist in jsonResponse:
            for track in playlist['tracks']:
                print('soundcloud: ' + track['title'])
                songList.append(Song('soundcloud', track['title'], track['permalink_url']))              
    else:
        playlistIds = soundcloudPlaylistToDownload.split('|')
        for playlistId in playlistIds:
            requestResponse = requests.get(soundcloudApiEndpoint + playlistId + 'playlists' + soundcloudClientId)
            jsonResponse = requestResponse.json()


    ####################  YouTube ####################
    # youTube fixed variables
    youtubeApiEndpoint = 'https://www.googleapis.com/youtube/v3/'

    # youTube env variables loaded
    youtubeChannelId = os.environ['youtubeChannelId']
    youtubeApiKey = os.environ['youtubeApiKey']
    youtubeDonwloadAllPlaylist = os.environ['youtubeDonwloadAllPlaylist']
    youtubePlaylistToDownload = os.environ['youtubePlaylistToDownload']

    if youtubeDonwloadAllPlaylist == 'Yes':
        pass       
    else:
        playlistIds = youtubePlaylistToDownload.split('|')
        for playlistId in playlistIds:
            payload = {'part':'snippet', 'maxResults':'50', 'playlistId':playlistId, 'key':youtubeApiKey}
            requestResponse = requests.get(youtubeApiEndpoint + 'playlistItems', params=payload)
            jsonResponse = requestResponse.json()
            for song in jsonResponse['items']:
                youtubeSongId = song['snippet']['resourceId']['videoId']
                youtubeSongTitle = song['snippet']['title']
                print('youtube: ' + youtubeSongTitle)
                songList.append(Song('youtube', youtubeSongTitle, 'https://www.youtube.com/watch?v=' + youtubeSongId))


    # Check s3 for repeats
    s3bucket = s3.Bucket(name=os.environ['s3bucket'])
    bucketList = []

    for item in s3bucket.objects.all():
        bucketList.append(item.key)
    print(bucketList)
    for song in songList:
        if song.title not in bucketList:
            print(song.title)
            lambdaPayload = {'service': song.service, 'songTitle': song.title, 'songUrl': song.url}
            lambdaClient.invoke(
                FunctionName=os.environ['downloadLambdafunction'],
                InvocationType='Event',
                Payload=json.dumps(lambdaPayload)
            )
            
    return len(songList)