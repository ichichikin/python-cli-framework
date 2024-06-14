import sys
import time
import marshal
import os
import logging
import hashlib
from system.utils import Utils
from system.config import Config


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
            user_input = input("Outdated cache is found. Remove? (y/n):")
            if user_input.lower() in ('y', 'yes'):
                for filename in to_remove:
                    os.remove(filename)
                logging.info("Outdated cache is removed")
            else:
                logging.info("Need to clean outdated cache")
    else:
        __cache = 0

    @classmethod
    def time(cls):
        return cls.__cache if cls.use_cache() else time.time()

    @classmethod
    def use_cache(cls):
        return cls.__cache > 0

    @classmethod
    def get(cls, obj: str):
        filename = hashlib.md5(obj.encode("utf8")).hexdigest() + ".mrsh"
        file = Utils.get_absolute_path("cache", filename)
        if os.path.isfile(file) is False:
            raise EmptyCacheException("No cache found: " + filename)
        else:
            with open(file, 'rb') as f:
                ret = marshal.load(f)
                logging.info("Cache loaded: " + filename)
                return ret

    @classmethod
    def set(cls, obj: str, value = None):
        filename = hashlib.md5(obj.encode("utf8")).hexdigest() + ".mrsh"
        file = Utils.get_absolute_path("cache", filename)
        with open(file, 'wb') as f:
            marshal.dump(value, f)
        logging.info("Cache created: " + filename)
        return value


class EmptyCacheException(Exception):
    pass
