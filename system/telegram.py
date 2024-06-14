from abc import abstractmethod, ABC


class Telegram(ABC):
    @abstractmethod
    def start(self) -> None:
        pass
