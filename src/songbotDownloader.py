import json, os
import youtube_dl
import boto3


s3client = boto3.resource('s3')

def songbotDownloader(event, context):
    service = event['service']
    songTitle = event['songTitle'].replace(" ", "_")
    songUrl = event['songUrl']
    print(event)


    class MyLogger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)


    def my_hook(d):
        print(d)
        if d['status'] == 'finished':
            print('Done downloading, now uplaoding ...')
            s3client.Object(os.environ['s3bucket'], songTitle.replace("_", " ")).put(Body=open(d['filename'], 'rb'))

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/tmp/'+songTitle+'.%(ext)s',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([songUrl])  
