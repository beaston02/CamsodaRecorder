# CamsodaRecorder

Automatically checks every 20 seconds (set in config file) to see which camsoda models are online and records any models which are in the "wanted" list when they are in a public shows. To auto record a model, add their username as found in the URL link to their chatroom (https://www.camsoda.com/{username}) to the "wanted" file.

I have only tested on Mac (10.10.4), although it should run on other opporating systems also.

Requires python3.5 or newer. You can grab python3.5.2 from https://www.python.org/downloads/release/python-352/

Requires one of the following:
livestreamer (https://github.com/chrippa/livestreamer)
streamlink (https://github.com/streamlink/streamlink)
ffmpeg (https://www.ffmpeg.org)


Edit the config.conf file to set your particular settings, and run with "python3.5 main.py" from within the root directory

While testing I had my IP address blocked by camsoda.com. I believe the issue was too many recordings running at once. At that time I was commonly recording 60+ models at a time. When I kept the number lower, I didnt experience any problems, so I believe the issue was the number of recordings and not the number of checks being done. as always, use this script at your own risk! 
