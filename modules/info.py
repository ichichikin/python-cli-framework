from system.app import App
from classes.log import Log
from system.config import *
from system.version import *
import sys
import json
import time
import platform
import os


class Info:
    def __init__(self):
        file_data = {}
        for root, dirs, files in os.walk(App.get_app_path(), topdown=True):
            if root.find(os.path.sep + ".") > -1 or root.find(os.path.sep + "__") > -1:
                continue
            file_data[root] = {os.path.join(root, name): os.stat(os.path.join(root, name)).st_size for name in files}

        Log.info(json.dumps({
                    "time": {"timestamp": time.time(), "utc_offset": -time.timezone},
                    "python": sys.version.split("\n"),
                    "execution": {"file": os.path.abspath(App.get_argv()[0]), "version": APP_VERSION},
                    "config": {k: v for k, v in Config.__dict__.items() if k[:2] != "__" and k[-2:] != "__"},
                    "system": platform.uname(),
                    "files": file_data
                }, sort_keys=False, indent=4)
        )
