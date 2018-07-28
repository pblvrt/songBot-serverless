import requests, json
import boto3
import os
# dynaodb client
dynamodb = boto3.resource(
    'dynamodb')

dbclient = dynamodb.Table(os.environ['ytVideos'])
# dbclient = dynamodb.Table('dev-ytVideos')
lambdaClient = boto3.client(
    'lambda')

def yt_api(event, context):

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
        # print(yt_id)
        # print(i)
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
                        'title': i['snippet']['title'],
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
            payload={'yt_id':yt_id}
            invoke = lambdaClient.invoke(
                    FunctionName='youtube-download-bot-dev-download',
                    InvocationType='Event',
                    Payload=json.dumps(payload)
                    )
            print(invoke)
