import os
import sys
import datetime
import time
from classes.camsoda import get, Config, Wanted, should_record_model, start_recording, RecordingThread

if __name__ == '__main__':
    r = get().requests_session()
    conf = Config(os.path.join(sys.path[0], 'config.conf'))
    Wanted = Wanted(conf.settings)
    next_run = datetime.datetime.now()
    while True:
        if datetime.datetime.now() < next_run:
            time.sleep(0.1)
            continue
        next_run += datetime.timedelta(seconds=conf.settings.interval)
        print("checking for online models")
        next_run += datetime.timedelta(seconds=conf.settings.interval)
        conf.refresh()
        online = get().online_models(r)
        if online:
            for model in online:
                if should_record_model(conf.settings).check(model):
                    start_recording(model, conf, r)
        else: next_run = datetime.datetime.now()
        print('finished check, next check in {} seconds'.format(conf.settings.interval))
        print('currently recording {} models: {}'.format(len(RecordingThread.currently_recording_models.keys())
                                                         ,list(RecordingThread.currently_recording_models.keys())))
