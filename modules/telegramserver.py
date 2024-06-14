import json
import time
from classes.log import Log
from flask import Flask, request, send_from_directory
import os
from requests import get, post
from system.config import Config
from classes.utils import Utils
from classes.telegramcontext import TelegramContext
import telegram
import urllib.parse


class TelegramServer:
    def __init__(self):
        all_commands = {}
        for module_name in telegram.__all__:
            module_name = module_name.split(".")
            root = telegram
            for module in module_name:
                root = getattr(root, module)
            for m in dir(root):
                if m.lower() == module_name[-1].lower():
                    inst = getattr(root, m)()
                    getattr(inst, 'start')()
                    for f in dir(getattr(root, m)):
                        if not f.startswith("_") and f != "start":
                            if f in all_commands:
                                Log.error("Telegram class " + module_name[-1] + " implements existing command: /" + f)
                            else:
                                all_commands[f.lower()] = module_name[-1]
                    break
            else:
                Log.error("Telegram class " + module_name[-1] + " has wrong format")
            break

        def call(command: str, chat_id: str, text: str) -> None:
            for module_name in telegram.__all__:
                module_name = module_name.split(".")
                root = telegram
                for module in module_name:
                    root = getattr(root, module)
                for m in dir(root):
                    if m.lower() == module_name[-1].lower():
                        for f in dir(getattr(root, m)):
                            if f == command:
                                ret = getattr(getattr(root, m), f)(TelegramContext(chat_id, command, text))
                                return ret
                        break

        Log.info("Starting Telegram server with commands: " + ", ".join(all_commands.keys()))

        domain = Utils.get_param("domain")

        if not domain:
            Log.error("Expecting 'domain' parameter to be specified")
            return

        get('https://api.telegram.org/bot' + Config.TELEGRAM_TOKEN + '/setWebhook?url=' + urllib.parse.quote_plus(domain + '/hidden_telegram_handler'))
        os.environ["FLASK_APP"] = Config.APP_NAME
        os.environ["FLASK_ENV"] = "development" if Config.DEBUG else "production"

        flask = Flask(Config.APP_NAME)

        if Config.ALLOW_WEB_ACCESS_TO_ETC:
            @flask.route('/<path:filename>')
            def assets(filename):
                Log.debug("Web access to " + filename)
                return send_from_directory(Utils.get_absolute_path('etc'), filename.replace("..", ""), as_attachment=True)

        @flask.errorhandler(Exception)
        def handle_http_exception(e):
            Log.warning("Web server exception", e)
            return "Hi, this is " + Config.APP_NAME, 200

        @flask.route("/hidden_telegram_handler", methods=['GET', 'POST'])
        def telegram_handler():
            req = request.get_json()
            if req and ("callback_query" in req):
                req = req["callback_query"]
                req["message"]["text"] = req["data"]
                post("https://api.telegram.org/bot" + Config.TELEGRAM_TOKEN + "/answerCallbackQuery", data={"callback_query_id": req["id"]})
            if req and "message" in req:
                chat_id = str(req["message"]["chat"]["id"])
                Log.debug("Telegram command from " + chat_id + ": " + req["message"]["text"])

                # timeout defence
                t = TelegramContext.static_get_memory(chat_id, "##timeout")
                if t and time.time() - t < .5:
                    post("https://api.telegram.org/bot" + Config.TELEGRAM_TOKEN + "/sendMessage", data={"chat_id": chat_id, "text": "Too frequent requests"})
                    return 'ok'

                # further execution
                mem_command = TelegramContext.static_get_memory(chat_id, "##command")
                if mem_command:
                    TelegramContext.static_set_memory(chat_id, "##command", None)
                    call(mem_command, chat_id, req["message"]["text"])
                else:
                    command = req["message"]["text"].lower()
                    sp = command.find(" ")
                    if sp >= 0:
                        command = command[0:sp]

                    if command[0] == '/':
                        command = command[1:]

                    if sp >= 0 and sp != len(req["message"]["text"]) - 1:
                        text_msg = req["message"]["text"][sp + 1:]
                    else:
                        text_msg = None

                    call(command, chat_id, text_msg)

                TelegramContext.static_set_memory(chat_id, "##timeout", time.time())

                t = TelegramContext.static_get_memory(chat_id, "##message")
                TelegramContext.static_set_memory(chat_id, "##message", None)

                k = TelegramContext.static_get_memory(chat_id, "##keyboard")
                TelegramContext.static_set_memory(chat_id, "##keyboard", None)

                if isinstance(t, str):
                    t = [t]
                elif t is None or t == "":
                    t = []
                for _t in t:
                    if len(_t) > 4096:
                        _t = _t[:4090] + "\n(...)"
                    if k:
                        post("https://api.telegram.org/bot" + Config.TELEGRAM_TOKEN + "/sendMessage", data={"chat_id": chat_id, "text": _t, "reply_markup": json.dumps(
                            {
                                "inline_keyboard": [[{"text": x, "callback_data": x}] for x in k], "one_time_keyboard": True
                            })
                        })
                    else:
                        post("https://api.telegram.org/bot" + Config.TELEGRAM_TOKEN + "/sendMessage", data={"chat_id": chat_id, "text": _t})

                if TelegramContext.static_get_memory(chat_id, "##command") is None:
                    post("https://api.telegram.org/bot" + Config.TELEGRAM_TOKEN + "/sendMessage", data={"chat_id": chat_id, "text": "Pick the command:", "reply_markup": json.dumps(
                        {
                            "inline_keyboard": [[{"text": x, "callback_data": x}] for x in all_commands.keys()], "one_time_keyboard": True
                        })
                    })
            return 'ok'

        flask.run(host='0.0.0.0', port=Config.TELEGRAM_WER_SERVER_PORT, debug=Config.DEBUG, use_reloader=False)
