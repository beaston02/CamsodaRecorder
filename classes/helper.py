

class url:
    online_api = 'https://www.camsoda.com/api/v1/browse/online'
    video_api = 'https://www.camsoda.com/api/v1/video/vtoken/{model}?username=guest_{num}'
    stream = 'https://{server}/cam/mp4:{stream_name}/playlist.m3u8?token={token}'
    user = 'https://www.camsoda.com/api/v1/user/{model}'

class rec_command:
    ffmpeg = 'ffmpeg -i {stream} -c copy {dl_path}'
    livestreamer = 'livestreamer --yes-run-as-root hlsvariant://{stream} best -f -o {dl_path}'
    streamlink = 'streamlink hlsvariant://{stream} best -o {dl_path}'