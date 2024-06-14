from system.app import App
from classes.log import Log
from abc import abstractmethod, ABC
import sys
import os


class Research(ABC):
    def __init__(self):
        Log.info("Started research with " + self.__class__.__name__)
        __target = sys._getframe(0).f_code.co_code
        __locals = {}

        def tracer(frame, event, arg):
            nonlocal __target
            nonlocal __locals
            if event == 'return' and __target == frame.f_back.f_code.co_code:
                __locals = frame.f_locals.copy()
        sys.setprofile(tracer)
        try:
            self.start()
        finally:
            sys.setprofile(None)

        Log.info("Research with " + self.__class__.__name__ + " is completed")

        if "self" in __locals:
            # del __locals["self"]
            frame_num = 1
            while True:
                try:
                    frame = sys._getframe(frame_num)
                    if os.path.abspath(frame.f_code.co_filename) == os.path.abspath(App.get_argv()[0]) and "__set_globals" in frame.f_globals:
                        frame.f_globals["__set_globals"](__locals)
                        break
                    frame_num += 1
                except:
                    break

    @abstractmethod
    def start(self) -> None:
        pass
