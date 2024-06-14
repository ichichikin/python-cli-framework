from system.logscollector import LogsCollector
from system.app import App
import re


class ConfigMeta(type):
    def __setattr__(self, *args):
        raise TypeError

    def __delattr__(self, *args):
        raise TypeError

    def __new__(mcs, name, base, ns):
        try:
            for argv in App.get_argv()[2:]:
                r = re.findall("^" + ns["__qualname__"] + "\\.([A-Za-z0-9]+)\\s*=\\s*(.*)$", argv)
                if len(r) == 0:
                    continue
                val = eval(r[0][1])
                if r[0][0] in ns:
                    LogsCollector.add("Config attribute is overridden: " + ns["__qualname__"] + "." + r[0][0] + " = " + str(r[0][1]), "info")
                ns[r[0][0]] = val
        except:
            LogsCollector.add("Config overrides have errors", "warning")

        return super().__new__(mcs, name, base, ns)
