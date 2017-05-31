import sys, datetime, time, os, threading
import urllib.request, json, random
from livestreamer import Livestreamer

#specify path to save to ie "/Users/Joe/camsoda"
save_directory = "/Users/Joe/camsoda"
#specify the path to the wishlist file ie "/Users/Joe/camsoda/wanted.txt"
wishlist = "/Users/Joe/camsoda/wanted.txt"


def getOnlineModels():
    num = random.randint(1000, 9999)
    wanted = []
    with open(wishlist) as f:
        for line in f:
            models = line.split()
            for theModel in models:
                wanted.append(theModel.lower())
    f.close()
    url = "https://www.camsoda.com/api/v1/browse/online"
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())
        for line in data['results']:
            if line['username'].lower() not in recording and line['status'] != 'connected':
                if line['display_name'].lower() in wanted or line['username'].lower() in wanted:
                    #if line['status'] == 'private':
                        #print("starting PRIVATE recording of ", line['display_name'])
                    #else:
                        #print("starting ", line['display_name'])
                    thread = threading.Thread(target=startRecording, args=(line, num))
                    thread.start()

def startRecording(modelData, num):
    try:
        recording.append(modelData['username'].lower())
        with urllib.request.urlopen(
                "https://www.camsoda.com/api/v1/video/vtoken/{model}?username=guest_{num}".format(model=modelData['username'], num=num)) as videoapi:
            data2 = json.loads(videoapi.read().decode())
            if str(modelData['status']) != 'limited':
                if str(modelData['status']) == 'private':
                    server = data2['private_servers'][0]
                elif modelData['status'] == 'online':
                    server = data2['edge_servers'][0]
                else:
                    server = data2['mjpeg_server']
                link = "hlsvariant://https://{server}/{app}/mp4:{stream_name}_mjpeg/playlist.m3u8?token={token}".format(server=server, app=data2['app'], stream_name=data2['stream_name'], token=data2['token'])
            if not os.path.exists("{path}/{model}".format(path=save_directory, model=modelData['username'])):
                os.makedirs("{path}/{model}".format(path=save_directory, model=modelData['username']))
            session = Livestreamer()
            streams = session.streams(link)
            stream = streams["best"]
            fd = stream.open()
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime("%Y.%m.%d_%H.%M.%S")
            with open("{path}/{model}/{st}_{model}.mp4".format(path=save_directory, model=modelData['username'], st=st), 'wb') as f:
                while True:
                    try:
                        data = fd.read(1024)
                        f.write(data)
                    except:
                        recording.remove(modelData['username'].lower())
                        #print("{} stream has ended".format(modelData['username']))
                        f.close()
                        return()
        recording.remove(modelData['username'].lower())
        #print("{} stream has ended".format(modelData['username']))

    except:
        recording.remove(modelData['username'].lower())
       # print("{} stream has ended".format(modelData['username']))

if __name__ == '__main__':
    recording = []
    while True:
        getOnlineModels()
        for i in range(30, 0, -1):
            sys.stdout.write("\033[K")
            print("{} model(s) are being recorded. Next check in {} seconds".format(len(recording), i))
            sys.stdout.write("\033[K")
            print("the following models are being recorded: {}".format(recording), end="\r")
            time.sleep(1)
            sys.stdout.write("\033[F")
