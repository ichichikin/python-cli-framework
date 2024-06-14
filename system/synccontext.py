from multiprocessing.managers import BaseManager, SyncManager
from system.config import Config
from typing import Any
import time
import signal
import sys
import os


# noinspection PyProtectedMember
class SyncContext:
    def get_context(self) -> dict:
        return self.__context

    def set_context(self, context: dict) -> None:
        self.__context = context

    def __init__(self):
        class CustomManager(BaseManager):
            pass

        CustomManager.register('get_int')
        CustomManager.register('remove_int')
        CustomManager.register('get_float')
        CustomManager.register('remove_float')
        CustomManager.register('get')
        CustomManager.register('remove_str')
        CustomManager.register('get_list')
        CustomManager.register('remove_list')
        CustomManager.register('get_dict')
        CustomManager.register('remove_dict')
        CustomManager.register('get_queue')
        CustomManager.register('remove_queue')
        CustomManager.register('lock_acquire')
        CustomManager.register('lock_release')
        self.__context = {}
        self.__throttler_time = 0
        self.__manager = CustomManager(address=('localhost', Config.SYNC_PORT), authkey=Config.APP_NAME.encode('utf-8'))
        try:
            self.__manager.connect()
        except Exception:
            self.__manager = SyncManager()
            self.__manager.start(self.__class__._manager_init)

    def get_int(self, name: str) -> Any:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            return self.__throttler(self.__manager.get_int, name)
        else:
            if (name := "int" + name.upper()) not in self.__context:
                self.__context[name] = self.__class__.__eof_handler(self.__manager.Value, 'i', 0)
            return self.__context[name]

    def remove_int(self, name: str) -> None:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            return self.__throttler(self.__manager.remove_int, name)
        else:
            if (name := "int" + name.upper()) in self.__context:
                del self.__context[name]

    def get(self, name: str) -> Any:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            return self.__throttler(self.__manager.get, name)
        else:
            if (name := "str" + name.upper()) not in self.__context:
                self.__context[name] = self.__class__.__eof_handler(self.__manager.Value, 'c', "")
            return self.__context[name]

    def remove_str(self, name: str) -> None:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            self.__throttler(self.__manager.remove_str, name)
        else:
            if (name := "str" + name.upper()) in self.__context:
                del self.__context[name]

    def get_float(self, name: str) -> Any:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            return self.__throttler(self.__manager.get_float, name)
        else:
            if (name := "float" + name.upper()) not in self.__context:
                self.__context[name] = self.__class__.__eof_handler(self.__manager.Value, 'd', 0.0)
            return self.__context[name]

    def remove_float(self, name: str) -> None:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            self.__throttler(self.__manager.remove_float, name)
        else:
            if (name := "float" + name.upper()) in self.__context:
                del self.__context[name]

    def get_list(self, name: str) -> Any:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            return self.__throttler(self.__manager.get_list, name)
        else:
            if (name := "list" + name.upper()) not in self.__context:
                self.__context[name] = self.__class__.__eof_handler(self.__manager.list)
            return self.__context[name]

    def remove_list(self, name: str) -> None:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            self.__throttler(self.__manager.remove_list, name)
        else:
            if (name := "list" + name.upper()) in self.__context:
                del self.__context[name]

    def get_dict(self, name: str) -> Any:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            return self.__throttler(self.__manager.get_dict, name)
        else:
            if (name := "dict" + name.upper()) not in self.__context:
                self.__context[name] = self.__class__.__eof_handler(self.__manager.dict)
            return self.__context[name]

    def remove_dict(self, name: str) -> None:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            self.__throttler(self.__manager.remove_dict, name)
        else:
            if (name := "dict" + name.upper()) in self.__context:
                del self.__context[name]

    def get_queue(self, name: str, *args) -> Any:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            return self.__throttler(self.__manager.get_queue, name, *args)
        else:
            if (name := "queue" + name.upper()) not in self.__context:
                self.__context[name] = self.__class__.__eof_handler(self.__manager.Queue, *args)
            return self.__context[name]

    def remove_queue(self, name: str) -> None:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            self.__throttler(self.__manager.remove_queue, name)
        else:
            if (name := "queue" + name.upper()) in self.__context:
                del self.__context[name]

    def lock_acquire(self, name: str) -> None:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            while not SyncContext.__get_value(self.__throttler, self.__manager.lock_acquire, name):
                time.sleep(0)
        else:
            if (name := "lock" + name.upper()) not in self.__context:
                self.__context[name] = self.__class__.__eof_handler(self.__manager.Lock)
            self.__class__.__eof_handler(self.__context[name].acquire)

    def lock_init(self, name: str) -> None:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            self.__throttler(self.__manager.lock_release, name)
        else:
            if (name := "lock" + name.upper()) in self.__context:
                self.__class__.__eof_handler(self.__context[name].release)

    def lock_release(self, name: str) -> None:
        name = name + Config.APP_NAME
        if self.__manager.__class__.__name__ == "CustomManager":
            self.__throttler(self.__manager.lock_release, name)
        else:
            if (name := "lock" + name.upper()) in self.__context:
                self.__class__.__eof_handler(self.__context[name].release)

    def get_int_copy(self, name: str) -> Any:
        return SyncContext.__get_value(self.get_int, name)

    def get_float_copy(self, name: str) -> Any:
        return SyncContext.__get_value(self.get_float, name)

    def get_copy(self, name: str) -> Any:
        return SyncContext.__get_value(self.get, name)

    def get_dict_copy(self, name: str) -> Any:
        return SyncContext.__get_value(self.get_dict, name)

    def get_list_copy(self, name: str) -> Any:
        return SyncContext.__get_value(self.get_list, name)

    def get_queue_copy(self, name: str, *args) -> Any:
        return SyncContext.__get_value(self.get_queue, name, *args)

    def __throttler(self, f, *args, **kwargs):
        for __attempts in range(Config.SYNC_ATTEMPTS):
            try:
                t = self.__throttler_time + Config.SYNC_THROTTLING_S - time.time()
                if self.__throttler_time and t > 0:
                    time.sleep(t)
                self.__throttler_time = time.time()
                return self.__class__.__eof_handler(f, *args, **kwargs)
            except OSError as e:
                if __attempts + 1 == Config.SYNC_ATTEMPTS:
                    try:
                        from classes.log import Log
                        from system.app import App
                        if App.is_master():
                            Log.error("Synchronization has failed", skip_sync=True)
                    except:
                        pass
                    try:
                        sys.exit(0)
                    except:
                        os._exit(0)
                else:
                    time.sleep(1)

    @staticmethod
    def __get_value(f, *args, **kwargs):
        return SyncContext.__eof_handler(f(*args, **kwargs)._getvalue)

    @staticmethod
    def __eof_handler(f, *args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (EOFError, ConnectionRefusedError, KeyboardInterrupt):
            try:
                from classes.log import Log
                from system.app import App
                if App.is_master():
                    Log.error("Synchronization has failed", skip_sync=True)
            except:
                pass
            try:
                sys.exit(0)
            except:
                os._exit(0)

    @staticmethod
    def _manager_init() -> None:
        signal.signal(signal.SIGINT, SyncContext._manager_signal_handler)
        sys.excepthook = SyncContext._manager_exception_hook


    @staticmethod
    def _manager_signal_handler() -> None:
        try:
            sys.exit(0)
        except:
            os._exit(0)

    @staticmethod
    def _manager_exception_hook(exc_type, exc_value, exc_traceback) -> None:
        if issubclass(exc_type, KeyboardInterrupt) or issubclass(exc_type, InterruptedError):
            try:
                sys.exit(0)
            except:
                os._exit(0)
