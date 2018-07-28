import json, os
import youtube_dl
import boto3


s3client = boto3.resource(
    's3',
    aws_access_key_id='AKIAJF4PHHPEM5U7DVGA',
    aws_secret_access_key='Odqbz4rRjZTQbCsDHxeQrv9ne+0c1yZlSwvZsH'
)
# def yt_downloader(event, context):
yt_id='5A6lMfCKME4'
# print(event)
# yt_id = event['yt_id']
# print (yt_id)

ydl_opts = {
'format': 'bestaudio/best',
'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192',
}],}
# 'outtmpl': '~/tmp'}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    meta = ydl.download(['https://www.youtube.com/watch?v=' + yt_id])

print( meta['title']
file_name = meta['title']
s3.Object('media-convert-outputs', file_name).put(Body=open(file_name, 'rb'))
