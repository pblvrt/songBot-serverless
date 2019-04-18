import json, os
import youtube_dl
import boto3


s3client = boto3.resource('s3')

def songbotDownloader(event, context):
    service = event['service'] # service can be youtube or soundcloud
    songTitle = event['songTitle'].replace(" ", "_")
    songUrl = event['songUrl']
    print(event)

    # Logger class for youtubeDl
    class MyLogger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)


    def hook(job):
        if job['status'] == 'finished':
            print('Done downloading, now uplaoding ...')
            try:
                s3client.Object(os.environ['s3bucket'], songTitle.replace("_", " ")).put(Body=open(job['filename'], 'rb'))
            except:
                print("Uplaod filed")
                return                

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/tmp/'+songTitle+'.%(ext)s',
        'logger': MyLogger(),
        'progress_hooks': [hook],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([songUrl])  
