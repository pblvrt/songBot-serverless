import os
import boto3
import requests
import json
from urllib.parse import unquote
# General
client = boto3.client('elastictranscoder')

def songbotTranscoder(event, context):
    key = unquote(event['Records'][0]['s3']['object']['key']).replace("+", " ")
    if key.endswith(".mp3"):
      return "Wont transcode mp3"
    else:
      response = client.create_job(
          PipelineId='1535198176673-7gwf3d',
          Input={'Key': key},
          Output={
            'Key': key + ".mp3",
            'PresetId': '1351620000001-300010'
          })
    return response