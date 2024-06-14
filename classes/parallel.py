import sys
import time
import multiprocessing as mp
from multiprocessing.pool import Pool as mpp
from multiprocessing import cpu_count
from typing import List, Union, Any, Callable, Iterable
from system.app import App


class NoDaemonProcess(mp.Process):
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, val):
        pass


class NoDaemonProcessPool(mpp):
    def Process(self, *args, **kwds):
        proc = super(NoDaemonProcessPool, self).Process(*args, **kwds)
        proc.__class__ = NoDaemonProcess
        return proc


class Parallel:
    def __init__(self, process_limit: int = cpu_count() - 1, process_timeout: int = 0):
        self.__handlers = {}
        self.__results = {}
        self.__process_limit = process_limit
        self.__process_timeout = process_timeout
        self.__next_process_uid = 0
        self.__pool = NoDaemonProcessPool(processes=self.__process_limit, initializer=Parallel._init, initargs=(App.get_argv(), App.get_instance_id(), App.get_context().get_context()))

        # as we use modified Pool of non-daemon processes, we create a separate process to terminate children on main process exit
        if len(App.get_context().get_list_copy("__processes")) == 0:
            App.get_context().get_list("__processes").append(mp.current_process().pid)
            self.__killer = NoDaemonProcess(target=self.__class__._killer, args=(mp.current_process().pid,))
            self.__killer.daemon = False

    def asynchronous_call(self, routine: Callable, args: Iterable = None, wait_until_worker_is_in_the_queue: bool = True, **kwargs) -> int:
        handler = self.__pool.apply_async(Parallel._wrapper, (args,), {'__routine': routine, **kwargs})
        process_uid = self.__next_process_uid
        self.__handlers[process_uid] = handler

        while True:
            for i, h in list(self.__handlers.items()):
                try:
                    self.__results[i] = h.get(timeout=0)
                    del self.__handlers[i]
                except mp.context.TimeoutError:
                    pass
            if wait_until_worker_is_in_the_queue and len(self.__handlers) > self.__process_limit:
                time.sleep(0.25)
            else:
                break

        counter = 0
        while True:
            if counter not in self.__results and counter not in self.__handlers:
                self.__next_process_uid = counter
                break
            counter += 1
        return process_uid

    @classmethod
    def synchronous_call(cls, routine: Callable, args: Iterable = None, **kwargs) -> Any:
        return routine(*args, **kwargs)

    @staticmethod
    def _init(cl: str, iid: str, context: dict) -> None:
        App.init(" ".join(cl), iid, context)
        App.get_context().get_list('__processes').append(mp.current_process().pid)

    @staticmethod
    def _killer(master_id: int) -> None:
        from system.synccontext import SyncContext
        import psutil
        context = SyncContext()
        if context is not None:
            try:
                time.sleep(1)
                while True:
                    if psutil.pid_exists(master_id):
                        for p in context.get_list('__processes').get_list_copy()[1:]:
                            for _p in psutil.process_iter():
                                if _p.pid == p:
                                    try:
                                        _p.kill()
                                    except:
                                        pass
                        break
                    time.sleep(1)
            except:
                pass

    @staticmethod
    def _wrapper(args: Iterable, **kwargs) -> Any:
        try:
            f = kwargs['__routine']
            del kwargs['__routine']
            if args:
                return f(*args, **kwargs)
            else:
                return f(**kwargs)
        except:
            from classes.log import Log
            Log.exception("Uncaught exception", exc_info=sys.exc_info())
            return None

    def get_processes_in_progress(self) -> int:
        for i, h in list(self.__handlers.items()):
            try:
                self.__results[i] = h.get(timeout=0)
                del self.__handlers[i]
            except mp.context.TimeoutError:
                pass

        return len(self.__handlers)

    def get_results(self, process_uid: int = None, timeout_s: float = None) -> Union[Any, List[Any]]:
        if process_uid:
            if process_uid in self.__results:
                ret = self.__results[process_uid]
                del self.__results[process_uid]
                return ret
            else:
                if process_uid in self.__handlers.keys():
                    ret = self.__handlers[process_uid].get(timeout=timeout_s)
                    del self.__handlers[process_uid]
                    return ret
        else:
            total_time = time.time()
            while len(self.__handlers):
                for i, h in list(self.__handlers.items()):
                    try:
                        self.__results[i] = h.get(timeout=0)
                        del self.__handlers[i]
                    except mp.context.TimeoutError:
                        pass
                if timeout_s and time.time() > total_time + timeout_s:
                    break
                else:
                    time.sleep(0.25)
            output = list(self.__results.values())
            self.__results = {}
            return output

    def close(self):
        if self.__pool:
            self.__pool.close()
            self.__pool.join()
            mp.active_children()
