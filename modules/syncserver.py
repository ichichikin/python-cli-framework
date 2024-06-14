from classes.log import Log
from queue import Queue
from multiprocessing.managers import BaseManager
from system.config import Config


class IntValue:
    def __init__(self, v: int = 0):
        self.__value = v

    def get(self) -> int:
        return self.__value

    def set(self, v: int) -> None:
        self.__value = v


class FloatValue:
    def __init__(self, v: float = 0.0):
        self.__value = v

    def get(self) -> float:
        return self.__value

    def set(self, v: float) -> None:
        self.__value = v


class StrValue:
    def __init__(self, v: str = ""):
        self.__value = v

    def get(self) -> str:
        return self.__value

    def set(self, v: str) -> None:
        self.__value = v


class SyncServer:
    def __init__(self):
        class CustomManager(BaseManager):
            pass

        class Context:
            def __init__(self):
                self.__context = {}

            def get_int(self, name: str) -> int:
                if (name := "int" + name.upper()) not in self.__context:
                    self.__context[name] = IntValue()
                return self.__context[name]

            def remove_int(self, name: str) -> None:
                if (name := "int" + name.upper()) in self.__context:
                    del self.__context[name]

            def get_float(self, name: str) -> float:
                if (name := "float" + name.upper()) not in self.__context:
                    self.__context[name] = FloatValue()
                return self.__context[name]

            def remove_float(self, name: str) -> None:
                if (name := "float" + name.upper()) in self.__context:
                    del self.__context[name]

            def get(self, name: str) -> str:
                if (name := "str" + name.upper()) not in self.__context:
                    self.__context[name] = StrValue()
                return self.__context[name]

            def remove_str(self, name: str) -> None:
                if (name := "str" + name.upper()) in self.__context:
                    del self.__context[name]

            def get_list(self, name: str) -> list:
                if (name := "list" + name.upper()) not in self.__context:
                    self.__context[name] = []
                return self.__context[name]

            def remove_list(self, name: str) -> None:
                if (name := "list" + name.upper()) in self.__context:
                    del self.__context[name]

            def get_dict(self, name: str) -> dict:
                if (name := "dict" + name.upper()) not in self.__context:
                    self.__context[name] = {}
                return self.__context[name]

            def remove_dict(self, name: str) -> None:
                if (name := "dict" + name.upper()) in self.__context:
                    del self.__context[name]

            def get_queue(self, name: str, *args) -> Queue:
                if (name := "queue" + name.upper()) not in self.__context:
                    self.__context[name] = Queue(*args)
                return self.__context[name]

            def remove_queue(self, name: str) -> None:
                if (name := "queue" + name.upper()) in self.__context:
                    del self.__context[name]

            def lock_acquire(self, name: str) -> bool:
                if (name := "lock" + name.upper()) not in self.__context:
                    self.__context[name] = True
                    return True
                else:
                    return False

            def lock_release(self, name: str) -> None:
                if (name := "lock" + name.upper()) in self.__context:
                    del self.__context[name]

        Log.info("Starting sync server")

        self.__context = {}
        context = Context()

        CustomManager.register('lock_acquire', callable=lambda name: context.lock_acquire(name))
        CustomManager.register('lock_release', callable=lambda name: context.lock_release(name))
        CustomManager.register('get_int', callable=lambda name: context.get_int(name))
        CustomManager.register('remove_int', callable=lambda name: context.remove_int(name))
        CustomManager.register('get_float', callable=lambda name: context.get_float(name))
        CustomManager.register('remove_float', callable=lambda name: context.remove_float(name))
        CustomManager.register('get', callable=lambda name: context.get_str(name))
        CustomManager.register('remove_str', callable=lambda name: context.remove_str(name))
        CustomManager.register('get_list', callable=lambda name: context.get_list(name))
        CustomManager.register('remove_list', callable=lambda name: context.remove_list(name))
        CustomManager.register('get_dict', callable=lambda name: context.get_dict(name))
        CustomManager.register('remove_dict', callable=lambda name: context.remove_dict(name))
        CustomManager.register('get_queue', callable=lambda name, *args: context.get_queue(name, *args))
        CustomManager.register('remove_queue', callable=lambda name: context.remove_queue(name))
        m = CustomManager(address=('localhost', Config.SYNC_PORT), authkey=Config.APP_NAME.encode('utf-8'))
        s = m.get_server()
        s.serve_forever()
