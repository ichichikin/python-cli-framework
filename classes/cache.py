import time
import marshal
import os
from classes.log import Log
import hashlib
from classes.utils import Utils
from system.config import Config
from system.exceptions import EmptyCacheException
from typing import Any


class Cache:
    __cache = Utils.get_param("cache")
    if __cache is not None:
        __cache = float(__cache)
        to_remove = []
        for file in os.listdir(os.fsencode(Utils.get_absolute_path("cache"))):
            filename = Utils.get_absolute_path("cache", os.fsdecode(file))
            if filename.endswith(".mrsh"):
                if os.path.getmtime(filename) + Config.CACHE_CLEAN_DELAY_DAYS * 60 * 60 * 24 < time.time():
                    to_remove.append(filename)

        if len(to_remove):
            for filename in to_remove:
                os.remove(filename)
            Log.debug("Outdated cache is removed")
    else:
        __cache = 0

    @classmethod
    def time(cls) -> float:
        return cls.__cache if cls.use_cache() else time.time()

    @classmethod
    def use_cache(cls) -> bool:
        return cls.__cache > 0

    @classmethod
    def get(cls, obj: str) -> Any:
        filename = hashlib.md5(obj.encode("utf8")).hexdigest() + ".mrsh"
        file = Utils.get_absolute_path("cache", filename)
        if os.path.isfile(file) is False:
            raise EmptyCacheException("No cache found: " + file)
        else:
            with open(file, 'rb') as f:
                ret = marshal.load(f)
                Log.debug("Cache loaded: " + filename)
                return ret

    @classmethod
    def set(cls, obj: str, value: object = None) -> object:
        filename = hashlib.md5(obj.encode("utf8")).hexdigest() + ".mrsh"
        file = Utils.get_absolute_path("cache", filename)
        with open(file, 'wb') as f:
            marshal.dump(value, f)
        Log.debug("Cache created: " + filename)
        return value
