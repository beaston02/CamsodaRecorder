import random
import requests
import os
import time
import datetime
import threading
import configparser
from colorama import Fore
from subprocess import Popen, PIPE, STDOUT, call
from classes import helper


class Settings():
    def __init__(self, parser, make_absolute):
        self._make_absolute = make_absolute
        self.conf_save_directory = parser.get('paths', 'save_directory')
        self.conf_wishlist_path = parser.get('paths', 'wishlist_path')
        self.conf_path_structure = parser.get('paths', 'path_structure')
        self.interval = parser.getint('settings', 'interval')
        self.recording_utility = parser.get('settings', 'recording_utility').lower()

    @property
    def save_directory(self):
        return self._make_absolute(self.conf_save_directory)

    @property
    def wishlist_path(self):
        return self._make_absolute(self.conf_wishlist_path)

    @property
    def path_structure(self):
        return self.conf_path_structure

class Config():
    def __init__(self, config_file_path):
        self._lock = threading.Lock()
        self._config_file_path = config_file_path
        self._parser = configparser.ConfigParser()
        self.refresh()

    @property
    def settings(self):
        return self._settings

    def _make_absolute(self, path):
        if not path or os.path.isabs(path):
            return path
        return os.path.join(os.path.dirname(self._config_file_path), path)

    def refresh(self):
        '''load config again to get fresh values'''
        self._parse()
        self._settings = Settings(self._parser, self._make_absolute)

    def _parse(self):
        with self._lock:
            self._parser.read(self._config_file_path)
class get():
    user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Mobile Safari/537.36'

    def online_models(self, r):
        try:
            data = r.get(helper.url.online_api).json()
        except: return None
        return data['results']

    def stream(self, model_data, r):
        num = random.randint(1000, 30000)
        video_data = r.get(helper.url.video_api.format(model=model_data['username'], num=num)).json()
        stream = helper.url.stream.format(server=video_data['edge_servers'][0],
                                    stream_name=video_data['stream_name'], model=model_data['username'],
                                    token=video_data['token'])
        return stream

    def requests_session(self):
        r = requests.session()
        r.headers.update({'user-agent':self.user_agent})
        r.get('http://www.camsoda.com')
        return(r)

class RecordingThread(threading.Thread):
    READING_BLOCK_SIZE = 1024
    currently_recording_models = {}
    total_data = 0
    file_count = 0
    _lock = threading.Lock()

    def __init__(self, model_data, config, r):
        super().__init__()
        self.model_data = model_data
        self.DEVNULL = open(os.devnull, 'wb')
        self.config = config
        self.currently_recording_models[model_data['username']] = model_data
        self.r = r
        print(Fore.GREEN + "started recording {}".format(self.model_data['display_name']) + Fore.RESET)

    @property
    def recording_models(self):
        return self.currently_recording_models

    def run(self):
        try:
            start_time = datetime.datetime.now()
            self.model_data['dl_path'] = self.create_path(self.config.settings.path_structure, start_time)
            self.model_data['stream'] = get().stream(model_data=self.model_data, r=self.r)
            os.makedirs(os.path.dirname(self.model_data['dl_path']), exist_ok=True)
            print(self.model_data['stream'])
            self.model_data['proc'] = Popen(self.build_command().split(), stdin=PIPE, stdout=self.DEVNULL,
                                            stderr=STDOUT)
            time.sleep(3)
            while self.model_data['proc'].poll() is None:
                time.sleep(1)


        except Exception as e:
            print('error in recording_models', e)
        finally:
            print(Fore.RED + "finished recording {}".format(self.model_data['display_name']) + Fore.RESET)
            try:self.currently_recording_models.pop(self.model_data['username'])
            except:pass

    def build_command(self):
        if self.config.settings.recording_utility == 'ffmpeg':
            return helper.rec_command.ffmpeg.format(**self.model_data)
        if self.config.settings.recording_utility == 'livestreamer':
            return helper.rec_command.livestreamer.format(**self.model_data)
        if self.config.settings.recording_utility == 'streamlink':
            return helper.rec_command.streamlink.format(**self.model_data)
        print('recording_utility is not defined, or is incorrect - options are: ffmpeg, livestreamer, streamlink')

    def recording_check(self):
        for model in self.currently_recording_models.keys():
            try:
                if os.stat(self.currently_recording_models[model['dl_path']]) < time.time() - 60:
                    self.currently_recording_models.pop(model)
            except:
                self.currently_recording_models.pop(model)

    def create_path(self, template, time):
        '''builds a recording-specific path from a template'''
        return template.format(
            path=self.config.settings.save_directory, model=self.model_data['username'],
            seconds=time.strftime("%S"), day=time.strftime("%d"),
            minutes=time.strftime("%M"), hour=time.strftime("%H"),
            month=time.strftime("%m"), year=time.strftime("%Y"))

def start_recording(model_data, settings, r):
    '''starts recording a session if it is not already being recorded'''
    already_recording = RecordingThread.currently_recording_models.get(model_data['username'])
    if not already_recording:
        RecordingThread(model_data, settings, r).start()
        return
    try:
        if os.stat(already_recording['dl_path']).st_mtime < time.time() - 300:
            RecordingThread(model_data, settings, r).start()
    except [FileNotFoundError, KeyError]: RecordingThread(model_data, settings, r).start()

class Wanted():
    def __init__(self, settings):
        self._lock = threading.RLock()
        self._settings = settings
        self._load()

    def _load(self):
        with self._lock:
            with open(self._settings.wishlist_path, 'r+') as file:
                self.wanted = file.readlines()
    @property
    def wanted_models(self):
        with open(self._settings.wishlist_path, 'r+') as file:
            self.wanted = [m.strip('\n') for m in file.readlines()]
            return self.wanted

class should_record_model():
    def __init__(self, settings):
        self._lock = threading.RLock()
        self._settings = settings
    def check(self, model):
        if model['username'] in Wanted(self._settings).wanted_models:
            if not hasattr(model,'status') or model['status'] == 'online':
                return True
        return False
