#!/usr/bin/env python3
"""
Python Tipee thingy

Description:
Display info about tipee timings
frank.villaro@infomaniak.com - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.
"""
import datetime
import os
import sys
import argparse

import requests

class CustomFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


def parse_time(str_time: str, default=None):
    if not str_time or str_time == "":
        return default
    return datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")


class Tipee:
    def __init__(self, instance: str):
        if instance[-1] != "/":
            instance += "/"
        self.instance = instance
        self.session = requests.Session()

    def login(self, username: str, password: str):
        url = self.instance + "api/sign-in"
        payload = {
            "username": username,
            "password": password,
        }
        r = self.session.post(url, json=payload)
        r.raise_for_status()

        self._get_me()

    def _get_me(self):
        url = self.instance + "brain/users/me"
        r = self.session.get(url)
        self.id = r.json()["id"]
        address_user = r.json()["address"]
        city_user = r.json()["city"]
        return address_user, city_user

    def get_timechecks(self, day=None):
        if not day:
            day = datetime.datetime.now()

        str_day = day.strftime("%Y-%m-%d")

        url = self.instance + f"api/employees/{self.id}/workday?date={str_day}"
        r = self.session.get(url)
        r.raise_for_status()

        js = r.json()
        return js.get("timechecks", [])

    def get_balances(self, day=None):
        if not day:
            day = datetime.datetime.today() - datetime.timedelta(days=1)

        str_day = day.strftime("%Y-%m-%d")

        url = self.instance + f"brain/plannings/soldes?day_end={str_day}"

        r = self.session.get(url)
        r.raise_for_status()

        js = r.json()
        return js

    def get_worktime(self, day=None):
        total_working_time = datetime.timedelta()

        for timecheck in self.get_timechecks(day):
            time_in = parse_time(timecheck["time_in"])
            time_out = parse_time(timecheck["time_out"] , datetime.datetime.now())
            if timecheck["time_out"] == None:
                time_out = parse_time(timecheck["proposal_out"], datetime.datetime.now())
            delta = time_out - time_in
            total_working_time += delta

        return total_working_time

    def get_birthdays(self):
        url = self.instance + "brain/persons/employee/birthday"
        r = self.session.get(url)
        r.raise_for_status()
        return (r.status_code == 200 and r.json()) or []

    def punch(self):
        url = self.instance + "brain/timeclock/timechecks"
        payload = {
            "person": self.id,
            "timeclock": "Linux",
        }
        r = self.session.post(url, json=payload)
        r.raise_for_status()

def get_weather():
    address_user, city_name = t._get_me()
    url_weater = f"http://wttr.in/{city_name}?0"
    response = requests.get(url_weater)        # To execute get request
    response_text = '\n' + response.text     # To print formatted JSON response
    return response_text

def parse_args(args=sys.argv[1:]):
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__, formatter_class=CustomFormatter
    )

    parser.add_argument('-p', '--punch', action='store_true', help="punch your time on Tipee")
    parser.add_argument('-d', '--no-departure', dest="no_departure", action='store_true', help="don't show you what time you can leave")
    parser.add_argument('-w', '--weather', action='store_true', help="show the current weather")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    t = Tipee(os.getenv("TIPEE_URL", default="https://infomaniak.tipee.net/"))
    username = os.getenv("TIPEE_USERNAME")
    password = os.getenv("TIPEE_PASSWORD")
    if username == None or password == None or username == '' or password == '':
        sys.exit("Please set TIPEE_USERNAME and TIPEE_PASSWORD environment variables")
    t.login(username, password)

    today = datetime.datetime.now()

    if args.punch:
        t.punch()
        print("The clock has been punched ! 🤜⏰")

    print(f'📅 TODAY {today.strftime("%Y-%m-%d")}\n-------------------\ntimes: ', end="")
    for timecheck in t.get_timechecks(today):
        for field in ["time_in", "time_out", "proposal_out"]:
            dt = parse_time(timecheck[field], None)
            if dt == None:
                pass
            elif field in ["proposal_out"]:
                print(f'\033[93m{dt.strftime("%H:%M")}\033[0m ', end="")
            elif dt is not None:
                print(f'\033[92m{dt.strftime("%H:%M")}\033[0m ', end="")
    worktime = t.get_worktime(today).total_seconds() // 60
    missing = 8 * 60 - worktime
    if missing < 0:
        missing = abs(missing)
        print(f"\ntotal worktime today so far: \033[1m{worktime // 60:.0f}h{worktime % 60:02.0f}m\033[0m ({missing // 60:.0f}h{missing % 60:02.0f}m over ⌛)")
    else:
        print(f"\ntotal worktime today so far: \033[1m{worktime // 60:.0f}h{worktime % 60:02.0f}m\033[0m ({missing // 60:.0f}h{missing % 60:02.0f}m left ⏳)")

    if not args.no_departure:
        # We take the second time_in and the first time_out
        nb_time_in = 0
        first_time_out = 0
        for timecheck in t.get_timechecks(today):
            time_in = parse_time(timecheck["time_in"])
            time_out = parse_time(timecheck["time_out"], datetime.datetime.now())
            nb_time_in += 1

            # we take the time_out as an int to calculate it
            if timecheck["time_out"] != None:
                first_time_out = 10000*datetime.datetime.strptime(timecheck["time_out"], "%Y-%m-%d %H:%M:%S").hour + 100*datetime.datetime.strptime(timecheck["time_out"], "%Y-%m-%d %H:%M:%S").minute
        # we take the time_in as an int to calculate it
        second_time_in = 10000*datetime.datetime.strptime(timecheck["time_in"], "%Y-%m-%d %H:%M:%S").hour + 100*datetime.datetime.strptime(timecheck["time_in"], "%Y-%m-%d %H:%M:%S").minute
        # we remove 30mins if we did not make the break
        if nb_time_in == 1:
            missing += 30
        elif nb_time_in == 2:
            diff = (second_time_in - first_time_out) / 100
            if diff >= 30:
                pass
            elif diff < 30:
                diff_pause = 30 - diff
                missing += diff_pause

        current_time = datetime.datetime.now()
        time_end_day = str(current_time + datetime.timedelta(minutes=missing))
        hour_end_day = "{:%Hh%Mm}".format(datetime.datetime.strptime(time_end_day, "%Y-%m-%d %H:%M:%S.%f"))
        if (worktime / 60) < 8:
            print(f"End of the day at: \033[1m{hour_end_day}\033[0m 🏃💨")
        else:
            print(f"End of the day at: \033[1mNOW GO GO GO\033[0m 🏃💨")


    balances = t.get_balances()
    print(f"\nbalance of hours before today: {int(balances['hours']['total'])}h{balances['hours']['total'] % 1 * 60:02.0f}m")
    print(f"balance of holidays before today: {balances['holidays']['remaining']}j")

    birthdays = [bd["first_name"] + " " + bd["last_name"] for bd in t.get_birthdays()]
    if len(birthdays) > 0:
        print(f'\n🎂 birthdays: {",".join(birthdays)}')

    # Weather
    if args.weather:
        print(get_weather())

# vim: set ts=4 sw=4 et:
