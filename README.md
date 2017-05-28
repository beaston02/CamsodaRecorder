# CamsodaRecorder

Automatically checks every 30 seconds to see which camsoda models are online and records any models which are in the "wanted" list when they are either in public shows, or private (spy, not ticket) shows. 

I have only tested on debian(7+8), and Mac (10.10.4), although it should run on other opporating systems also.

Requires python3.5 or newer. You can grab python3.5.2 from https://www.python.org/downloads/release/python-352/

Requires livestreamer (https://github.com/chrippa/livestreamer)

While testing I had my IP address blocked by camsoda.com. I believe the issue was too many recordings running at once. At that time I was commonly recording 60+ models at a time. When I kept the number lower, I didnt experience any problems, so I believe the issue was the number of recordings and not the number of checks being done. as always, use this script at your own risk! 
