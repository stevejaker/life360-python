#!/usr/bin/env python3

import time
import json
import fuzzy
import requests


class Error(Exception):
    pass

class CircleNotFoundError(Error):
    pass

class InvalidDataTypeError(Error):
    pass

class InvalidScanTypeError(Error):
    pass

class Location(object):
    """
    """
    def __init__(self):
        self.lat = 0.0
        self.lon = 0.0
        self.pin = ""
        self.address = ""
        self.since = 0
        self.last_updated = 0
        self.accuracy = 0
        self.in_transit = False
        self.is_driving = False

    def _update(self, other):
        if type(other) == dict:
            self._update_from_dct(other)
        else:
            self._update_from_obj(other)

    def _update_from_obj(self, other):
        self.lat = other.lat
        self.lon = other.lon
        self.pin = other.pin
        self.address = other.address
        self.since = other.since
        self.last_updated = other.last_updated
        self.accuracy = other.accuracy

    def _update_from_dct(self, location):
        self.address = self._format_address(location["address1"], location["address2"])
        self.lat = self._check_type(location["latitude"], typ="float")
        self.lon = self._check_type(location["longitude"], typ="float")
        self.accuracy = self._check_type(location["accuracy"], typ="int")
        self.since = self._check_type(location["since"], typ="int")
        self.last_updated = self._check_type(location["timestamp"], typ="int")
        self.in_transit = self._check_type(location["inTransit"], typ="bool")
        self.speed = self._check_type(location["speed"], typ="int")
        self.is_driving = self._check_type(location["isDriving"], typ="bool")
        self.set_pin()

    def _check_type(self, var, typ="str"):
        if typ == "int":
            try:
                # Value can be a LONG string. Converting to float first prevents
                # LOTS of errors
                return int(float(var))
            except:
                raise InvalidDataTypeError(f"{var} could not be converted to int")
        elif typ == "float":
            try:
                return float(var)
            except:
                raise InvalidDataTypeError(f"{var} could not be converted to float")
        elif typ == "bool":
            if str(var) == "1":
                return True
            else:
                return False
        else:
            return str(var)

    def _format_address(self, address1, address2):
        # Often and address cannot be determined by Life360
        if address1 is None or address2 is None:
            return "Not Found"
        else:
            # There can be a lot of whitespace in these addresses
            return f"{address1.strip()} {address2.strip()}".strip()

    def set_pin(self):
        self.pin = f"http://maps.google.com/maps?q={self.lat},{self.lon}&z=13"

    def print_vars(self):
        print(f"    lat: {self.lat}")
        print(f"    lon: {self.lon}")
        print(f"    pin: {self.pin}")
        print(f"    address: {self.address}")
        print(f"    since: {self.since}")
        print(f"    last_updated: {self.last_updated}")
        print(f"    accuracy: {self.accuracy}")
        print(f"    in_transit: {self.in_transit}")
        print(f"    is_driving: {self.is_driving}")

    def get_coords(self):
        return f"{self.lat}, {self.lon}"

    def get_pin(self):
        return self.pin

    def get_address(self):
        return self.address

    def get_time_at_location(self):
        return f"Since {time.ctime(self.since)}"

    def get_lat_lon(self):
        return self.lat, self.lon


class Person(object):
    """
    """
    tolerence = 0.001
    def __init__(self, data=None):
        self.id = None
        self.first = None
        self.last = None
        self.current_location = Location()
        self.former_location = Location()
        self.battery = 0
        self.is_charging = False
        self.high_battery_color = '\033[92m' # Green
        self.mid_battery_color = '\033[33m' # Yellow
        self.low_battery_color = '\033[31m' # Red
        self.color_reset = '\033[0m' # Resets terminal output
        self.high_battery_threshold = 75 # Threshold for high battery
        self.low_battery_threshold = 25 # Threshold for low battery
        if data is not None:
            self.update(data)

    def _get_color(self): #DONE
        if self.battery >= self.high_battery_threshold or self.is_charging:
            return self.high_battery_color, self.color_reset
        elif self.battery >= self.low_battery_threshold:
            return self.mid_battery_color, self.color_reset
        else:
            return self.low_battery_color, self.color_reset

    def _update_location(self, location):
        self.former_location._update(self.current_location)
        self.current_location._update(location)

    def normalize_name(self):
        # There can be lots of whitespace
        return f"{self.first.strip()} {self.last.strip()}".strip()

    def get_id(self):
        return self.id

    def get_battery_level(self, use_color=False): #DONE
        charging = ''
        if self.is_charging:
            charging = ' and charging'
        if use_color:
            color, reset = self._get_color()
            return f"{color}{self.battery}%{charging}{reset}"
        else:
            return f"{self.battery}%{charging}"

    def get_current_location(self):
        pass

    def get_former_location(self):
        pass

    def update(self, data):
        if type(data) != dict:
            raise InvalidDataTypeError(f"{type(data)} was recieved. Life360 circle dictionary must be recieved.")
        self._update_location(data["location"])
        if self.first is None:
            self.first = data["firstName"]
        if self.last is None:
            self.last = data["lastName"]
        if self.id is None:
            self.id = data["id"]
        self.battery = int(data["location"]["battery"])
        self.is_charging = bool(int(data["location"]["charge"]))
        # self.using_wifi = data["location"]["wifiState"]

    def summary(self):
        is_moving = self.check_movement()
        if is_moving:
            msg = "Moving"
        else:
            msg = "Stationary"
        print(f"Name: {self.normalize_name()} -- Battery level: {self.get_battery_level(use_color=True)}")
        print(f"    Current Location: {msg} near {self.current_location.get_address()} ({self.current_location.get_coords()})")
        print(f"    Current Pin: {self.current_location.get_pin()}")
        print(f"    {self.current_location.get_time_at_location()}")
        # print(f"    Former Location: {self.former_location.get_address()} ({self.former_location.get_coords()})")
        # print(f"    Former Pin: {self.former_location.get_pin()}")

    def print_vars(self):
        print(f"first: {self.first}")
        print(f"last: {self.last}")
        print(f"current_location:")
        self.current_location.print_vars()
        print(f"former_location:")
        self.former_location.print_vars()
        print(f"battery: {self.battery}")
        print(f"is_charging: {self.is_charging}")
        print(f"high_battery_color: {self.high_battery_color}")
        print(f"mid_battery_color: {self.mid_battery_color}")
        print(f"low_battery_color: {self.low_battery_color}")
        print(f"color_reset: {self.color_reset}")
        print(f"high_battery_threshold: {self.high_battery_threshold}")
        print(f"low_battery_threshold: {self.low_battery_threshold}")

    def check_movement(self):
        clat, clon = self.current_location.get_lat_lon()
        flat, flon = self.former_location.get_lat_lon()
        if (abs(flat) + self.tolerence) < clat < (abs(flat) - self.tolerence):
            return True
        elif (abs(flon) + self.tolerence) < clon < (abs(flon) - self.tolerence):
            return True
        return False


class life360(object):
    """
    """
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
        self.people       = {}
        self.scan         = False
        self.delay        = 10
        if self.token is None:
            self.setDefaultToken()

    def setDefaultToken(self): #DONE
        self.token = "cFJFcXVnYWJSZXRyZTRFc3RldGhlcnVmcmVQdW1hbUV4dWNyRUh1YzptM2ZydXBSZXRSZXN3ZXJFQ2hBUHJFOTZxYWtFZHI0Vg=="

    def make_request(self, url, data=None, method='GET', authheader=None): #DONE
        headers = {'Accept': 'application/json'}
        if authheader:
            headers.update({'Authorization': authheader, 'cache-control': "no-cache",})
        if method == 'GET':
            r = requests.get(url, headers=headers)
        elif method == 'POST':
            r = requests.post(url, data=data, headers=headers)
        return r.json()

    def save_circle_data(self, data): #DONE
        for circle in data:
            name = circle['name']
            soundex = self.soundex(name)
            id = circle['id']
            self.circles[name] = id
            self.circles[soundex] = id

    def get_id_from_name(self, name): #DONE
        soundex = self.soundex(name)
        if name in self.circles:
            return self.circles[name]
        elif soundex in self.circles:
            return self.circles[soundex]
        else:
            raise CircleNotFoundError(f"Unable to locate circle with name: '{name}'")

    def authenticate(self): #DONE
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

    def get_all_circles(self): #DONE
        url = self.base_url + self.circles_url
        authheader = f"bearer {self.access_token}"
        r = self.make_request(url, method='GET', authheader=authheader)
        self.save_circle_data(r['circles'])
        return r['circles']

    def get_circle_by_id(self, circle_id): #DONE
        url = self.base_url + self.circle_url + circle_id
        authheader = f"bearer {self.access_token}"
        r = self.make_request(url, method='GET', authheader=authheader)
        return r

    def get_circle_by_name(self, name): #DONE
        id = self.get_id_from_name(name)
        return self.get_circle_by_id(id)

    def _update(self, id):
        data = self.get_circle_by_id(id)
        for person_data in data["members"]:
            person_id = person_data["id"]
            person = self.people[person_id]
            person.update(person_data)

    def _add_person(self, person_data): #DONE
        person = Person(person_data)
        # id = person.get_id()
        id = person_data["id"]
        self.people[id] = person

    def _populate_people_list(self, id): #DONE
        data = self.get_circle_by_id(id)
        for person_data in data["members"]:
            self._add_person(person_data)

    def scan_circle(self, id=None, name=None, max_scans=100):
        self.scan=True
        scan_num = 0
        if name is not None:
            id = get_id_from_name(name)
        elif id is None:
            raise InvalidScanTypeError("No circle selected to scan.")
        self._populate_people_list(id)

        while scan_num < max_scans:
            self._update(id)
            # self.print_vars()
            self.person_summary()
            scan_num +=1
            print("Completed scan number: ", scan_num)
            time.sleep(self.delay)

    def print_vars(self):
        for id, person in self.people.items():
            person.print_vars()
            print()

    def person_summary(self):
        for id, person in self.people.items():
            person.summary()
            print()
