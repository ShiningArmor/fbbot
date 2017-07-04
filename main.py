# -*- coding: utf-8 -*-
    
import os
import logging
import logging.handlers
from colorlogging import ColorFormatter
from flask import Flask, request, make_response
from facebookbot import FBAgent
from bot import Bot
import json


def get_logger(name, debug=False):
    LOG_FILENAME = name + ".out"
    logFormatter = ColorFormatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger('%sLogger' % name[:name.find(".")].capitalize())
    logger.setLevel(logging.DEBUG)
    fileHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1048576, backupCount=5, )
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)
    if debug:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        logger.addHandler(consoleHandler)
    return logger


class FlaskBot(Flask):
    def __init__(self, name):
        super(self.__class__, self).__init__(name)
        self.log = get_logger("bot", True)
        self.settings = json.loads(open("settings.json").read())
        self.bot = Bot("testingBot")
        self.facebook_agent = FBAgent(self.settings)



app = FlaskBot(__name__)


@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        try:
            if request.args.get("hub.verify_token") == app.settings["VERIFY_TOKEN"]:
                app.log.debug("#(green)VERIFY TOKEN: %s" % str(request.args.get("hub.verify_token")))
                return request.args.get("hub.challenge")
            else:
                return 'Invalid verification token'
        except Exception as e:
            return str(e)

    if request.method == 'POST':
        output = request.get_json()

        try:
            if output.get("log"):
                return open("logfile.txt").read()

            for event in output['entry']:
                messaging = event['messaging']
                for msg in messaging:
                    if msg.get('message'):
                        recipient_id = msg['sender']['id']
                        app.log.debug("#(green)%s" % str(msg['message']))
                        if msg['message'].get('text'):
                            message = msg['message']['text']
                            response = app.bot.ask(message)
                            app.log.debug("#(green)fbID: %s - response: %s" % str(recipient_id), str(response))
                            app.facebook_agent.bot.send_text_message(recipient_id, response)
                        if msg['message'].get('attachment'):
                            app.facebook_agent.bot.send_attachment_url(recipient_id,
                                                                       msg['message']['attachment']['type'],
                                                                       msg['message']['attachment']['payload']['url'])
                    else:
                        return make_response("TEST: %s " % msg["test"], 200)
            return "Success"
        except Exception as e:
            app.log.error(str(e))
            return make_response("Error:\n %s\n\n" % str(e), 204)


def main():
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
