import json, os
import youtube_dl
import boto3


s3client = boto3.resource('s3')

def yt_downloader(event, context):
    print(event)
    yt_id = event['yt_id']
    title = event['title']
    print(title + '' + title)
    
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
        meta = ydl.download(['https://www.youtube.com/watch?v=' + yt_id])

    s3client.Object('media-convert-outputs', title +'mp3').put(Body=open('tmp/'+ yt_id+'.mp3', 'rb'))
