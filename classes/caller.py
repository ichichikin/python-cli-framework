from system.app import App
from classes.parallel import Parallel
import subprocess
import sys
import re
from multiprocessing import cpu_count
from typing import List, Union, Optional


class Caller:
    def __init__(self, process_limit: int = cpu_count() - 1, process_timeout: int = 0):
        self.__process_limit = process_limit
        self.__process_timeout = process_timeout
        self.__parallel = Parallel(self.__process_limit, self.__process_timeout)

    def asynchronous_call(self, command_line: str, regexp_filter: str = "", wait_until_worker_is_in_the_queue: bool = False) -> int:
        return self.__parallel.asynchronous_call(self._worker, (command_line, regexp_filter), wait_until_worker_is_in_the_queue=wait_until_worker_is_in_the_queue)

    @classmethod
    def synchronous_call(cls, command_line: str, regexp_filter: str = "") -> List[str]:
        return cls._worker(command_line, regexp_filter)

    def get_processes_in_progress(self) -> int:
        return self.__parallel.get_processes_in_progress()

    def get_results(self, pid: int = None, timeout_s: float = None) -> Union[List[str], List[List[str]]]:
        return self.__parallel.get_results(pid, timeout_s)

    @staticmethod
    def _worker(command_line: str, regexp_filter: str) -> Optional[List[str]]:
        try:
            if regexp_filter:
                ret = re.findall(regexp_filter, subprocess.run(
                    [sys.executable, App.get_app_path(), command_line],
                    stdout=subprocess.PIPE
                ).stdout.decode('utf-8'), re.M | re.S)
            else:
                ret = subprocess.run(
                    [sys.executable, App.get_app_path(), command_line],
                    stdout=subprocess.PIPE
                ).stdout.decode('utf-8')
            return ret
        except:
            return

    def close(self):
        self.__parallel.close()
