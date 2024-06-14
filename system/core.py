import modules
from classes.log import Log
from classes.utils import Utils
from system.version import APP_VERSION
from system.config import Config
from system.app import App


class Core:
    __initialized: bool = False

    def __init__(self):
        assert not Core.__initialized, "The Core class must have only one instance"
        Core.__initialized = True

        if Utils.get_param("no_greetings") in [None, "0", "false", "no"]:
            Log.info("Hi, this is " + Config.APP_NAME + " " + APP_VERSION + ": " + (" ".join(App.get_argv()[1:]) if len(App.get_argv()) > 1 else "[no params]"))

        if len(App.get_argv()) < 2:
            Log.error("Specify some module to launch")
        else:
            for module_name in modules.__all__:
                if module_name.lower() == App.get_argv()[1].lower():
                    module = getattr(modules, module_name)
                    for m in dir(module):
                        if m.lower() == module_name.lower():
                            getattr(module, m)()
                            break
                    else:
                        Log.error("Specified module has wrong format")
                    break
            else:
                Log.error("Specified module is not found")

        if Utils.get_param("no_greetings") in [None, "0", "false", "no"]:
            Log.info("Bye")
