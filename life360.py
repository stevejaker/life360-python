#!/usr/bin/env python3

import json
import fuzzy
import requests

class Error(Exception):
    pass

class CircleNotFoundError(Error):
    pass


class life360:
    base_url = "https://api.life360.com/v3/"
    token_url = "oauth2/token.json"
    circles_url = "circles.json"
    circle_url = "circles/"

    def __init__(self, token=None, email=None, password=None):
        self.soundex      = fuzzy.Soundex(4)
        self.token        = token
        self.email        = email
        self.password     = password
        self.access_token = None
        self.circles      = {}

    def make_request(self, url, data=None, method='GET', authheader=None):
        headers = {'Accept': 'application/json'}
        if authheader:
            headers.update({'Authorization': authheader, 'cache-control': "no-cache",})
        if method == 'GET':
            r = requests.get(url, headers=headers)
        elif method == 'POST':
            r = requests.post(url, data=data, headers=headers)
        return r.json()

    def save_circle_data(self, data):
        for circle in data:
            name = circle['name']
            soundex = self.soundex(name)
            id = circle['id']
            self.circles[name] = id
            self.circles[soundex] = id

    def get_id_from_name(self, name):
        soundex = self.soundex(name)
        if name in self.circles:
            return self.circles[name]
        elif soundex in self.circles:
            return self.circles[soundex]
        else:
            raise CircleNotFoundError(f"Unable to locate circle with name: '{name}'")


    def authenticate(self):
        url = self.base_url + self.token_url
        data = {
            "grant_type": "password",
            "username":   self.email,
            "password":   self.password,
        }
        authheader = f"Basic {self.token}"
        r = self.make_request(url, data=data, method='POST', authheader=authheader)
        if 'access_token' in r:
            self.access_token = r['access_token']
            return True
        else:
            return False

    def get_all_circles(self):
        url = self.base_url + self.circles_url
        authheader = f"bearer {self.access_token}"
        r = self.make_request(url, method='GET', authheader=authheader)
        self.save_circle_data(r['circles'])
        return r['circles']

    def get_circle_by_id(self, circle_id):
        url = self.base_url + self.circle_url + circle_id
        authheader = f"bearer {self.access_token}"
        r = self.make_request(url, method='GET', authheader=authheader)
        return r

    def get_circle_by_name(self, name):
        id = self.get_id_from_name(name)
        return self.get_circle_by_id(id)
