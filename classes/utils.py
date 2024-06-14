import json
import os
import time
from typing import Optional, Any
from system.app import App
from system.config import Config


class Utils:
    __initialized = False
    __lock_initialized = False

    @staticmethod
    def get_param(param: str, save_case: bool = False) -> Optional[str]:
        for argv in App.get_argv()[2:]:
            if argv.lower().startswith(param.lower() + "="):
                return argv[len(param) + 1:] if save_case else argv.lower()[len(param) + 1:]
        else:
            return None

    @classmethod
    def get_setting(cls, param: str) -> Optional[Any]:
        cls.__load_setting()

        cp = App.get_context().get_dict_copy("settings")
        for k in cp.keys():
            if k.startswith("%%") and App.get_context().get_dict("settings").get(k, time.time() + 1) < time.time():
                App.get_context().get_dict("settings").update({k: None})
                App.get_context().get_dict("settings").update({k[2:]: None})

        return App.get_context().get_dict("settings").get(param, None)

    @classmethod
    def set_setting(cls, param: str, value: Any, seconds_to_live: int = 0) -> None:
        assert not param.startswith("%%"), "Param name must not start with %%"
        cls.__load_setting()

        if not Config.FORBID_MULTIPROCESSING_OVERHEAD:
            App.get_context().lock_acquire("settings")
        try:
            if seconds_to_live != 0:
                App.get_context().get_dict("settings").update({"%%" + param: time.time() + seconds_to_live})
            App.get_context().get_dict("settings").update({param: value})

            with open(cls.get_absolute_path("data", "settings.json"), "w") as write_file:
                cp = App.get_context().get_dict_copy("settings")
                for k in list(cp.keys()):
                    if cp[k] is None:
                        del cp[k]

                json.dump(cp, write_file)
        finally:
            if not Config.FORBID_MULTIPROCESSING_OVERHEAD:
                App.get_context().lock_release("settings")

    @classmethod
    def get_absolute_path(cls, *argv: str) -> str:
        return os.path.join(App.get_app_path(), *argv)

    @classmethod
    def __load_setting(cls) -> None:
        if not cls.__initialized:
            cls.__initialized = True
            if not cls.__lock_initialized and App.is_master():
                App.get_context().lock_init("settings")
                cls.__lock_initialized = True
            if not Config.FORBID_MULTIPROCESSING_OVERHEAD:
                App.get_context().lock_acquire("settings")
            try:
                with open(cls.get_absolute_path("data", "settings.json"), "r") as read_file:
                    App.get_context().get_dict("settings").update(json.load(read_file))
            finally:
                if not Config.FORBID_MULTIPROCESSING_OVERHEAD:
                    App.get_context().lock_release("settings")
