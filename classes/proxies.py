import requests
import time
from classes.log import Log
from system.config import Config
from classes.utils import Utils
from typing import List
import re


class Proxies:
    @staticmethod
    def update() -> None:
        obj = requests.get("http://account.fineproxy.org/api/getproxy/?format=txt&type=httpauth&login=" + Config.PROXY_LOGIN + "&password=" + Config.PROXY_PASSWORD)
        if obj.status_code != 200 or not re.match("([\d\.]+:\d+)", obj.text):
            Log.debug("Can not update proxies")
            return

        with open(Utils.get_absolute_path("data", "proxies.txt"), "w") as write_file:
            write_file.write(obj.text)

    @staticmethod
    def get(skip_update: bool = False) -> List[str]:
        if not skip_update:
            uts = Utils.get_setting("proxy_update_ts")
            if uts is None or uts + Config.CHECK_FOR_NEW_PROXIES_S <= time.time() and Config.PROXY_LOGIN != "" and Config.PROXY_PASSWORD != "":
                Utils.set_setting("proxy_update_ts", time.time())
                Log.debug("Updating proxies")
                Proxies.update()

        try:
            with open(Utils.get_absolute_path("data", "proxies.txt"), "r") as read_file:
                obj = [x.replace("\r", "").replace("\n", "") for x in read_file]
        except:
            obj = []
        return obj
