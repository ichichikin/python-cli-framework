from classes.utils import Utils
from typing import Optional, Any, Union
from system.config import Config


class TelegramContext:
    def __init__(self, chat_id: str, command: str, users_text: str):
        self.__chat_id = chat_id
        self.__command = command
        self.__text = users_text

    def get_memory(self, key: str) -> Any:
        return self.__class__.static_get_memory(self.__chat_id, key)

    def set_memory(self, key: str, value: Optional[Any]) -> None:
        assert not key.startswith("##") and not key.startswith("%%"), "Key must not start with ## or %%"
        self.__class__.static_set_memory(self.__chat_id, key, value)

    def say(self, message: Union[str, list], route_back: bool = False, keyboard: Optional[list] = None) -> None:
        if route_back:
            self.__class__.static_set_memory(self.__chat_id, "##command", self.__command)
        if keyboard:
            self.__class__.static_set_memory(self.__chat_id, "##keyboard", keyboard)
        self.__class__.static_set_memory(self.__chat_id, "##message", message)

    def get_text(self) -> str:
        return self.__text

    @staticmethod
    def static_get_memory(chat_id: str, key: str) -> Any:
        key = chat_id + "|" + key
        return Utils.get_setting(key)

    @staticmethod
    def static_set_memory(chat_id: str, key: str, value: Optional[Any] = None) -> None:
        key = chat_id + "|" + key
        Utils.set_setting(key, value, Config.TELEGRAM_MEMORY_TIME_DAYS * 24 * 60 * 60)
