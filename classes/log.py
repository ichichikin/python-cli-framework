#######################################################################################################################
# Logging class
# TODO: fix file rotation
#######################################################################################################################

from logging.handlers import RotatingFileHandler
from system.logscollector import LogsCollector
import logging
import sys
import io
import colorama
import re
from system.config import Config
from classes.utils import Utils
from system.app import App
from typing import Optional


# noinspection PyProtectedMember
class Log:
    __path_len = len(App.get_app_path()) + 1
    __instance_id = ""
    __logger = logging.getLogger()

    @classmethod
    def setup_logger(cls, root: bool = False, instance_id: str = "") -> logging.Logger:
        class ColorFormatter(logging.Formatter):
            def __init__(self, format_pattern: str):
                super().__init__()
                self.__formats = {
                    logging.DEBUG: re.sub(r'(%[^%]*?levelname.*?s)', colorama.Fore.LIGHTBLUE_EX + '\\1' + colorama.Fore.RESET, format_pattern),
                    logging.INFO: re.sub(r'(%[^%]*?levelname.*?s)', colorama.Fore.LIGHTGREEN_EX + '\\1' + colorama.Fore.RESET, format_pattern),
                    logging.WARNING: re.sub(r'(%[^%]*?levelname.*?s)', colorama.Fore.LIGHTYELLOW_EX + '\\1' + colorama.Fore.RESET, format_pattern),
                    logging.ERROR: re.sub(r'(%[^%]*?levelname.*?s)', colorama.Fore.LIGHTRED_EX + '\\1' + colorama.Fore.RESET, format_pattern),
                    logging.CRITICAL: re.sub(r'(%[^%]*?levelname.*?s)', colorama.Fore.RED + '\\1' + colorama.Fore.RESET, format_pattern)
                }

            def format(self, record):
                return logging.Formatter(self.__formats[record.levelno], "%d.%m.%Y %H:%M:%S").format(record)

        colorama.init()

        if App.is_master():
            App.get_context().lock_init("logger" + Config.APP_NAME)

        if not Config.FORBID_MULTIPROCESSING_OVERHEAD:
            App.get_context().lock_acquire("logger" + Config.APP_NAME)

        try:

            logger = logging.getLogger("general_logger") if root is False else logging.getLogger()
            logger.setLevel(logging.DEBUG if Config.DEBUG else logging.INFO)

            if Config.DEBUG:
                cls.__instance_id = instance_id
                if len(instance_id):
                    instance_id = '%(instance_id)s '
                if root:
                    format_str = instance_id + '%(asctime)s.%(msecs)03d %(levelname)-7s > %(message)s [%(module)s:%(lineno)d]'  # @%(thread)d
                else:
                    format_str = instance_id + '%(asctime)s.%(msecs)03d %(levelname)-7s > %(message)s [%(file)s:%(line)d]'  # @%(thread)d
            else:
                if root:
                    format_str = '%(asctime)s.%(msecs)03d %(levelname)-7s > %(message)s [%(module)s:%(lineno)d]'
                else:
                    format_str = '%(asctime)s.%(msecs)03d %(levelname)-7s > %(message)s [%(file)s:%(line)d]'

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(ColorFormatter(format_str))
            logger.handlers = []

            try:
                file_handler = RotatingFileHandler(Utils.get_absolute_path("logs", "app.log"), encoding='utf-8', maxBytes=Config.MAX_LOG_FILE_SIZE_BYTES, backupCount=Config.LOG_FILE_BACKUP)
                file_handler.setFormatter(ColorFormatter(format_str))
                logger.addHandler(file_handler)
            except:
                LogsCollector.add("Failed to set file logger", "warning")

            logger.propagate = False
            logger.addHandler(console_handler)
            cls.__logger = logger

        finally:
            if not Config.FORBID_MULTIPROCESSING_OVERHEAD:
                App.get_context().lock_release("logger" + Config.APP_NAME)

        return logger

    @classmethod
    def warning(cls, msg, *args, **kwargs) -> Optional[str]:
        return cls.__log(cls.__logger.warning, msg, *args, **kwargs)

    @classmethod
    def info(cls, msg, *args, **kwargs) -> Optional[str]:
        return cls.__log(cls.__logger.info, msg, *args, **kwargs)

    @classmethod
    def error(cls, msg, *args, **kwargs) -> Optional[str]:
        if 'exc_info' in kwargs:
            return cls.__log(cls.__logger.exception, msg, *args, **kwargs)
        else:
            return cls.__log(cls.__logger.error, msg, *args, **kwargs)

    @classmethod
    def debug(cls, msg, *args, **kwargs) -> Optional[str]:
        return cls.__log(cls.__logger.debug, msg, *args, **kwargs)

    @classmethod
    def exception(cls, msg, *args, **kwargs) -> Optional[str]:
        ret = cls.__log(cls.__logger.exception, msg, *args, **{'return_only': True, **kwargs})
        if 'exc_info' in kwargs:
            del kwargs['exc_info']
        ret = cls.__log(cls.__logger.error, ret, *args, **{'skip_formatting': True, **kwargs})
        return ret

    @classmethod
    def get_logger(cls) -> logging.Logger:
        return cls.__logger

    @classmethod
    def __log(cls, func: callable, msg, *args, **kwargs) -> Optional[str]:
        return_only = False
        skip_formatting = False
        skip_sync = False
        handlers = []
        formatters = []
        log_stream = None
        log_stream_handler = None
        frame_level = 2
        if "frame_level" in kwargs:
            if kwargs["frame_level"]:
                frame_level = kwargs["frame_level"]
            del kwargs["frame_level"]
        if "return_only" in kwargs:
            if kwargs["return_only"]:
                return_only = True
            del kwargs["return_only"]
        if "skip_formatting" in kwargs:
            if kwargs["skip_formatting"]:
                skip_formatting = True
            del kwargs["skip_formatting"]
        if "skip_sync" in kwargs:
            if kwargs["skip_sync"]:
                skip_sync = True
            del kwargs["skip_sync"]

        if not Config.FORBID_MULTIPROCESSING_OVERHEAD and not skip_sync:
            App.get_context().lock_acquire("logger" + Config.APP_NAME)

        try:
            if return_only:
                handlers = cls.__logger.handlers
                log_stream = io.StringIO()

                cls.__logger.handlers = []
                log_stream_handler = logging.StreamHandler(log_stream)
                log_stream_handler.setFormatter(handlers[0].formatter)
                cls.__logger.addHandler(log_stream_handler)

            if skip_formatting:
                for h in cls.__logger.handlers:
                    formatters.append(h.formatter)
                    h.setFormatter(logging.Formatter("%(message)s"))

            frame = sys._getframe(frame_level)
            if len(cls.__instance_id) and isinstance(msg, str):
                msg = msg.split("\n")
                for i, m in enumerate(msg[1:]):
                    msg[i + 1] = cls.__instance_id + " >> " + m
                msg = "\n".join(msg)

            try:
                msg = msg % (*args,)
            except TypeError:
                msg = " ".join([str(i) for i in [msg, *args]])

            try:
                func(msg, **kwargs, extra={
                    'file': frame.f_code.co_filename[cls.__path_len:],
                    'line': frame.f_lineno,
                    'instance_id': cls.__instance_id
                })
            except PermissionError:
                pass

            if skip_formatting:
                for i, h in enumerate(cls.__logger.handlers):
                    h.setFormatter(formatters[i])

            if return_only:
                cls.__logger.removeHandler(log_stream_handler)
                for h in handlers:
                    cls.__logger.addHandler(h)
                ret = log_stream.getvalue()[:-1]
            else:
                ret = None

        finally:
            if not Config.FORBID_MULTIPROCESSING_OVERHEAD and not skip_sync:
                App.get_context().lock_release("logger" + Config.APP_NAME)

        if ret is not None:
            return ret
