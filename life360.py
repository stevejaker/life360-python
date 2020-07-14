#!/usr/bin/env python3

import json
import requests

class life360:
    base_url = "https://api.life360.com/v3/"
    token_url = "oauth2/token.json"
    circles_url = "circles.json"
    circle_url = "circles/"

    def __init__(self, token=None, user_email=None, password=None):
        self.token        = token
        self.user_email   = user_email
        self.password     = password
        self.access_token = None

    def make_request(self, url, data=None, method='GET', authheader=None):
        headers = {'Accept': 'application/json'}
        if authheader:
            headers.update({'Authorization': authheader, 'cache-control': "no-cache",})
        if method == 'GET':
            r = requests.get(url, headers=headers)
        elif method == 'POST':
            r = requests.post(url, data=data, headers=headers)
        return r.json()

    def authenticate(self):
        url = self.base_url + self.token_url
        data = {
            "grant_type": "password",
            "user_email":   self.user_email,
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
        return r['circles']

    def get_circle_by_id(self, circle_id):
        url = self.base_url + self.circle_url + circle_id
        authheader = f"bearer {self.access_token}"
        r = self.make_request(url, method='GET', authheader=authheader)
        return r
