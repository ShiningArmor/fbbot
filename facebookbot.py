# -*- coding: utf-8 -*-
import requests
import json
from pymessenger.bot import Bot

class FBAgent(object):
    def __init__(self, settings):
        self.access_token = settings["ACCESS_TOKEN"]
        self.bot = Bot(self.access_token)

    def get_user_info(self,user_id):
        url =  "https://graph.facebook.com/v2.6/<USER_ID>"
        url += "?fields=first_name,last_name,profile_pic,locale,timezone,gender"
        url += "&access_token=<PAGE_ACCESS_TOKEN>"
        url = url.replace("<USER_ID>", user_id).replace("<PAGE_ACCESS_TOKEN>", self.access_token)
        response = requests.get(url)
        print response.__dict__
        data = response.json()
        return data