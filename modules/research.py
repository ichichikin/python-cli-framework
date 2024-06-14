from system.app import App
from classes.log import Log
import researches
import os


class Research:
    def __init__(self):
        if len(App.get_argv()) < 3:
            Log.error("Specify some research name to run")
        else:
            param = App.get_argv()[2].replace(os.sep, ".")
            for module_name in researches.__all__:
                if module_name.lower() == param.lower():
                    module_name = module_name.split(".")
                    root = researches
                    for module in module_name:
                        root = getattr(root, module)
                    for m in dir(root):
                        if m.lower() == module_name[-1].lower():
                            getattr(root, m)()
                            break
                    else:
                        Log.error("Specified research has wrong format")
                    break
            else:
                Log.error("Specified research is not found")
