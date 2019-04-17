import json, os
import youtube_dl
import boto3


s3client = boto3.resource('s3')

def songbotDownloader(event, context):
    service = event['service']
    songTitle = event['songTitle']
    songUrl = event['songUrl']
    print(event)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/tmp/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([songUrl])
    s3client.Object(os.environ['s3bucket'], songTitle +'mp3').put(Body=open('tmp/'+ songTitle +'.mp3', 'rb'))
