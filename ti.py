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
            time_out = parse_time(timecheck["time_out"], datetime.datetime.now())

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


def parse_args(args=sys.argv[1:]):
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__, formatter_class=CustomFormatter
    )

    subparsers = parser.add_subparsers(help='Punch your time')
    parser_a = subparsers.add_parser('punch')
    parser_a.add_argument('--punch', default=True)

    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args()

    t = Tipee(os.getenv("TIPEE_URL", default="https://infomaniak.tipee.net/"))
    username = os.getenv("TIPEE_USERNAME")
    password = os.getenv("TIPEE_PASSWORD")
    if username is None or password is None:
        sys.exit("Please set TIPEE_USERNAME and TIPEE_PASSWORD environment variables")
    t.login(username, password)

    today = datetime.datetime.now()

    if 'punch' in args:
        t.punch()
        print("The clock has been punched ! 🤜⏰")

    print(f'📅 TODAY {today.strftime("%Y-%m-%d")}\n-------------------\ntimes: ', end="")
    for timecheck in t.get_timechecks(today):
        for field in ["time_in", "time_out"]:
            dt = parse_time(timecheck[field], None)
            if dt is not None:
                print(f'{dt.strftime("%H:%M")} ', end="")
    worktime = t.get_worktime(today).total_seconds() // 60
    missing = 8 * 60 - worktime
    if missing < 0:
        missing = abs(missing)
        print(f"\ntotal worktime today so far: {worktime // 60:.0f}h{worktime % 60:02.0f}m ({missing // 60:.0f}h{missing % 60:02.0f}m over ⌛)")
    else:
        print(f"\ntotal worktime today so far: {worktime // 60:.0f}h{worktime % 60:02.0f}m ({missing // 60:.0f}h{missing % 60:02.0f}m left ⏳)")

    balances = t.get_balances()
    print(f"\nbalance of hours before today: {int(balances['hours']['total'])}h{balances['hours']['total'] % 1 * 60:02.0f}m")
    print(f"balance of holidays before today: {balances['holidays']['remaining']}j")

    birthdays = [bd["first_name"] + " " + bd["last_name"] for bd in t.get_birthdays()]
    if len(birthdays) > 0:
        print(f'\n🎂 birthdays: {",".join(birthdays)}')

# vim: set ts=4 sw=4 et:
