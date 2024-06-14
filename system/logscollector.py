from typing import List, Tuple


class LogsCollector:
    __logs = []

    @classmethod
    def add(cls, msg: str, t: str = "info") -> None:
        cls.__logs.append((msg, t))

    @classmethod
    def get(cls) -> List[Tuple]:
        return cls.__logs
