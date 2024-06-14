import signal
import sys
import time
import random
import string
import multiprocessing as mp
import importlib.util
import os


class App:
    __logger = None
    __original_sigint = None
    __instance_id = None
    __alive = False
    __argv = []
    __path = None
    __master_process = True
    __context = None

    @classmethod
    def init(cls, command_line: str = None, instance_id: str = None, context: dict = None) -> None:
        assert cls.__original_sigint is None, "The App class must have only one instance"

        if instance_id is None:
            print("Loading...", end="\r")
        else:
            cls.__master_process = False

        from system.logscollector import LogsCollector

        # calculating command line state
        import re
        if command_line:
            cls.__argv = [sys.argv[0]]
            for split in re.split("\\s", command_line):
                if len(split):
                    cls.__argv += [split]
        else:
            cls.__argv = sys.argv

        # calculating app's path
        from system.config import Config
        try:
            import system.version as ver

            spec = importlib.util.spec_from_file_location("version", os.path.join(os.path.dirname(cls.__argv[0]), "system", "version.py"))
            test = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test)
            if test.APP_VERSION != ver.APP_VERSION:
                raise Exception

            cls.__path = os.path.abspath(os.path.dirname(cls.__argv[0]))
        except:
            name = re.sub("[^\\w]", "", Config.APP_NAME.lower())
            if not len(name):
                name = "framework"
            import tempfile
            cls.__path = os.path.abspath(os.path.join(tempfile.gettempdir(), name))

            for d in ["data", "logs", "cache"]:
                try:
                    os.makedirs(os.path.join(cls.__path, d))
                except:
                    pass

            LogsCollector.add("App's path is set to the temporary storage", "warning")

        # setting up multiprocessing context
        if Config.DEBUG and instance_id is None:
            import multiprocessing
            multiprocessing.set_start_method("spawn")

        from system.synccontext import SyncContext
        cls.__context = SyncContext()
        if context is not None:
            cls.__context.set_context(context)

        if cls.__master_process:
            cls.__instance_id = str(int(time.time() * 1000))[-11::2] + ''.join(random.choices(string.ascii_uppercase, k=3))  # this is the master process
        else:
            cls.__instance_id = instance_id + "-" + str(int(time.time() * 1000))[-11::2] + ''.join(random.choices(string.ascii_uppercase, k=3))  # this is a slave process, adding an unique process id

        # setting up loggers
        from classes.log import Log
        Log.setup_logger(instance_id=cls.__instance_id)

        if command_line and not mp.parent_process():
            Log.info("Command line is overridden: " + " ".join(cls.__argv))
        for log in LogsCollector.get():
            if log[1] == "warning":
                Log.warning(log[0])
            elif log[1] == "error":
                Log.error(log[0])
            elif log[1] == "exception":
                Log.exception(log[0])
            else:
                Log.info(log[0])

        # setting up handlers
        def signal_handler(sig, frame) -> None:
            if cls.__master_process:
                Log.error("Stopped with Ctrl+C", skip_sync=True)

            cls.__alive = False
            if not Config.SOFT_CTRL_C:
                try:
                    sys.exit(0)
                except:
                    os._exit(0)
            # signal.signal(signal.SIGINT, cls.__original_sigint)

        cls.__original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal_handler)

        def exception_handler(exc_type, exc_value, exc_traceback) -> None:
            if issubclass(exc_type, KeyboardInterrupt) or issubclass(exc_type, InterruptedError):
                # sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            Log.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback), skip_sync=True)

        sys.excepthook = exception_handler
        del App.init

    @classmethod
    def start(cls) -> None:
        # launching the core behavior
        del App.start
        cls.__alive = True

        from system.core import Core
        Core()

        cls.__alive = False

    @classmethod
    def exit(cls, code: int) -> None:
        from classes.log import Log

        cls.__alive = False
        Log.info("Exited, bye", skip_sync=True)
        try:
            sys.exit(code)
        except:
            os._exit(code)

    @classmethod
    def is_alive(cls):
        return cls.__alive

    @classmethod
    def is_master(cls):
        return cls.__master_process

    @classmethod
    def get_instance_id(cls) -> str:
        return cls.__instance_id

    @classmethod
    def get_argv(cls) -> list:
        return cls.__argv

    @classmethod
    def get_app_path(cls) -> str:
        return cls.__path

    @classmethod
    def get_context(cls) -> 'SyncContext':
        return cls.__context
