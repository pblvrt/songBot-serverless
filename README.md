# songBot

songBot is an AWS serverless bot that downloads full playlist out of soundCloud and youtube into a s3 bucket.

songBot uses [youtube-dl](https://youtube-dl.org/) to make the downloading from both sites possible.

## Installation:

* git clone this repo.
* Install the [serverless framework](https://serverless.com/framework/docs/providers/aws/guide/installation/).
* Fill out env.yml:
⋅⋅⋅ Add your google api key and a soundcloud clientID.
⋅⋅⋅ You can point the bot to any youtube channel by specifying the youtube channel Id.
⋅⋅⋅ If **soundcloudDownloadAllPlaylist** or **soundcloudDownloadAllPlaylist** is set to True, the bot will download all public ⋅⋅⋅playlist of the channels specified, if is set to False, the bot will only download off the playlist specified in ⋅⋅⋅**soundcloudPlaylistToDownload** and **youtubePlaylistToDownload**
* Once you are done configuring the env variables, just `sls dèploy`and you will be ready to go.

## Notes:

* The bot runs on a cron job which by default runs daily, you can change this in the serverless.yaml file.
