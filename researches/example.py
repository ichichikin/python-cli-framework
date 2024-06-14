from system.research import *
from classes.log import Log


class Example(Research):
    def start(self) -> None:
        Log.info("This is the sample research file")
