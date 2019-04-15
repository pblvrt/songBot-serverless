import requests, json
import boto3
import os

# aws clients
dynamodb = boto3.resource('dynamodb')
dbclient = dynamodb.Table(os.environ['ytVideos'])
lambdaClient = boto3.client('lambda')

def yt_api(event, context):
    # soundcloud api calls
    #soundcloud details
    soundcloudUserId = 'users/580297311'
    soundcloudClientId = '/playlists?client_id=xIa292zocJP1G1huxplgJKVnK0V3Ni9D'
    soundcloudApiEndpoint = 'http://api.soundcloud.com/'

    #get all playlist and then tracks
    request = soundcloudApiEndpoint + soundcloudUserId + soundcloudClientId
    requestResponse = requests.get(soundcloudApiEndpoint + soundcloudUserId + soundcloudClientId)
    #requestResponse = requests.get('http://api.soundcloud.com/users/580297311/playlists?client_id=xIa292zocJP1G1huxplgJKVnK0V3Ni9D')
    print(request)
    jsonResponse = requestResponse.json()

    for playlist in jsonResponse:
        print(playlist['permalink'])
        for track in playlist['tracks']:
            print('\t'+ track['title'] + '\n\t' + track['permalink_url'] + '\n')


    # youtbe api call
    yt_data_api = 'https://www.googleapis.com/youtube/v3/playlistItems'
    part = 'snippet'
    playlistId = os.environ['playlistId']
    key = os.environ['key']
    payload = {'part':part, 'maxResults':'50', 'playlistId':playlistId, 'key':key}
    r = requests.get(yt_data_api, params=payload)

    # write to dynamo
    var = json.loads(r.text)
    for i in var['items']:
        yt_id = i['snippet']['resourceId']['videoId']
        title = i['snippet']['title']
        response = dbclient.get_item(Key={'yt_id': yt_id})
        if 'Item' in response:
            print(yt_id + ' video already exists')
        else:
            try:
                dbclient.put_item(
                    Item={
                        'yt_id': yt_id,
                        'publishedAt': i['snippet']['publishedAt'],
                        'channelId': i['snippet']['channelId'],
                        'title': title,
                        'description': i['snippet']['description'],
                        'thumbnails': i['snippet']['thumbnails']
                    }
                )
                print('added ' + yt_id)
            except Exception as e:
                try:
                    dbclient.put_item(Item={'yt_id':yt_id})
                    print('added ' + yt_id)
                except:
                    pass

            # invoke lambda for each new song. pass song ID
            payload={'yt_id':yt_id,
                     'title': title}

            invoke = lambdaClient.invoke(
                    FunctionName='youtube-download-bot-dev-download',
                    InvocationType='Event',
                    Payload=json.dumps(payload)
                    )
            print(invoke)
