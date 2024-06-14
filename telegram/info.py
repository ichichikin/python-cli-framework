import subprocess
import re
from classes.utils import Utils
from system.telegram import Telegram
from classes.telegramcontext import TelegramContext


class Info(Telegram):
    def start(self) -> None:
        pass

    @staticmethod
    def temperature(context: TelegramContext) -> None:
        try:
            ret = subprocess.run(["sensors"], stdout=subprocess.PIPE).stdout.decode('utf-8')
        except:
            ret = "Cannot retrieve the temperature"
        context.say(ret)

    @staticmethod
    def data_directory(context: TelegramContext) -> None:
        try:
            ret = subprocess.run(["ls", "-laH", Utils.get_absolute_path("data")], stdout=subprocess.PIPE).stdout.decode('utf-8')
        except:
            ret = "Cannot retrieve content of data directory"
        context.say(ret)

    @staticmethod
    def research_status(context: TelegramContext) -> None:
        text = context.get_text() if context.get_text() else ""
        try:
            with open(Utils.get_absolute_path("logs", "app.log")) as f:
                lines = f.readlines()
        except:
            context.say("Cannot retrieve status")
            return

        res = {}
        errors = []
        non_errors = []
        had_error = False
        for i, l in enumerate(lines):
            lines[i] = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', "", l)
            r = re.match(r'^([A-Z0-9\-]+).*?\s>\sStarted research with ([A-Za-z0-9_]+)', lines[i])
            if r:
                r = r.groups()
                res[r[1]] = r[0]

            if re.match(r'^([A-Z0-9\-]+)\s>>\s', lines[i]):
                if had_error and len(errors) > 0:
                    errors[-1] = errors[-1] + "\n" + lines[i]
                elif not had_error and len(non_errors) > 0:
                    non_errors[-1] = non_errors[-1] + "\n" + lines[i]
            else:
                had_error = True if re.match(r'^[A-Z0-9\-]+[^A-Za-z]+\sERROR\s', lines[i]) else False
                if had_error:
                    errors.append(lines[i])
                else:
                    non_errors.append(lines[i])

        # ищем нужный ID по всем сообщениям
        r = re.match(r'[A-Za-z0-9_]+\s\(([A-Z0-9\-]+)\)$', text.upper())
        id = None
        if r:
            id = r.groups()[0]
            if id in res.values():
                indexes_to_remove = []
                for i, msg in enumerate(non_errors):
                    if re.match(r'^' + id + r'[\s\-]', msg) is None:
                        indexes_to_remove.insert(0, i)
                for i in indexes_to_remove:
                    del non_errors[i]
                indexes_to_remove = []
                for i, msg in enumerate(errors):
                    if re.match(r'^' + id + r'[\s\-]', msg) is None:
                        indexes_to_remove.insert(0, i)
                for i in indexes_to_remove:
                    del errors[i]
        if text.lower() == "everything" or id in res.values():
            if text.lower() == "everything":
                del non_errors[-1]

            counter = 0
            message_len = 0
            for x in reversed(non_errors):
                counter += 1
                non_errors[-counter] = re.sub(r'^[A-Z0-9\-]+\s', "", x)
                message_len += len(non_errors[-counter]) + 1
                if message_len - 1 > 4096:
                    counter -= 1
                    break
            str_result = "\n".join(non_errors[-counter:])

            result = ["Found log records (" + str(len(non_errors)) + " total):", str_result]

            if len(errors):
                counter = 0
                message_len = 0
                for x in reversed(errors):
                    counter += 1
                    errors[-counter] = re.sub(r'^[A-Z0-9\-]+\s', "", x)
                    message_len += len(errors[-counter]) + 1
                    if message_len - 1 > 4096:
                        counter -= 1
                        break
                str_result = "\n".join(errors[-counter:])

                result += ["Found errors (" + str(len(errors)) + " total):", str_result]
            else:
                result += ["No errors were found"]

            context.say(result)
        else:
            res_list = []
            for k, v in res.items():
                res_list.append(k + " (" + v + ")")

            context.say("What research status do you need?", True, res_list[-10:] + ["Everything"])
