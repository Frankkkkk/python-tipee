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
        self._cache = {}

    def _request(self, url, payload=None):
        if url in self._cache:
            return self._cache[url]

        if payload:
            r = self.session.post(self.instance + url, json=payload)
        else:
            r = self.session.get(self.instance + url)
        r.raise_for_status()
        if r.text.strip():  # tipee likes to reply with a single empty line
            self._cache[url] = r.json()
            return self._cache[url]

    def login(self, username: str, password: str):
        self._request("api/sign-in", payload = {
            "username": username,
            "password": password,
        })
        self.id = self._request("brain/users/me")["id"]

    def get_timechecks(self, day=None):
        if not day:
            day = datetime.datetime.now()

        str_day = day.strftime("%Y-%m-%d")

        data = self._request(f"api/employees/{self.id}/workday?date={str_day}")

        for timecheck in data.get("timechecks", []):
            timecheck["in"] = parse_time(timecheck["proposal_in"] or timecheck["time_in"])
            timecheck["out"] = parse_time(timecheck["proposal_out"] or timecheck["time_out"])
            yield timecheck

    def get_balances(self, day=None):
        if not day:
            day = datetime.datetime.today() - datetime.timedelta(days=1)

        str_day = day.strftime("%Y-%m-%d")

        return self._request(f"brain/plannings/soldes?day_end={str_day}")

    def get_worktime(self, day=None) -> datetime.timedelta:
        total_working_time = datetime.timedelta()

        for timecheck in self.get_timechecks(day):
            out = timecheck["out"] or datetime.datetime.today()
            delta = out - timecheck["in"]
            total_working_time += delta

        return total_working_time

    def get_birthdays(self):
        data = self._request("brain/persons/employee/birthday")
        return data or []

    def punch(self):
        self._request("brain/timeclock/timechecks", payload = {
                "person": self.id,
                "timeclock": "Linux",
            })


def parse_args(args=sys.argv[1:]):
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__, formatter_class=CustomFormatter
    )

    parser.add_argument("--no-departure", dest="show_departure", action="store_false", help="Don't show suggested departure time")
    subparsers = parser.add_subparsers(help='Punch your time')
    parser_a = subparsers.add_parser('punch')
    parser_a.add_argument('--punch', default=True)

    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args()

    t = Tipee(os.getenv("TIPEE_URL", default="https://infomaniak.tipee.net/"))
    username = os.getenv("TIPEE_USERNAME")
    password = os.getenv("TIPEE_PASSWORD")
    if username == None or password == None or username == '' or password == '':
        sys.exit("Please set TIPEE_USERNAME and TIPEE_PASSWORD environment variables")
    t.login(username, password)

    today = datetime.datetime.now()

    if 'punch' in args:
        t.punch()
        print("The clock has been punched ! 🤜⏰")

    print(f'📅 TODAY {today.strftime("%Y-%m-%d")}\n-------------------\ntimes: ', end="")
    for timecheck in t.get_timechecks(today):
        if timecheck["proposal_in"]:
            print(f"\033[93m", end="")
        else:
            print(f"\033[92m", end="")
        print(timecheck["in"].strftime("%H:%M"), end="")
        print("\033[0m-", end="")

        if timecheck["out"]:
            if timecheck["proposal_out"]:
                print(f"\033[93m", end="")
            else:
                print(f"\033[92m", end="")
            print(timecheck["out"].strftime("%H:%M"), end="")
            print("\033[0m", end="")
        else:
            print("…", end="")

    worktime = t.get_worktime(today).total_seconds() // 60
    missing = 8 * 60 - worktime
    if missing < 0:
        missing = abs(missing)
        print(f"\ntotal worktime today so far: \033[1m{worktime // 60:.0f}h{worktime % 60:02.0f}m\033[0m ({missing // 60:.0f}h{missing % 60:02.0f}m over ⌛)")
    else:
        print(f"\ntotal worktime today so far: \033[1m{worktime // 60:.0f}h{worktime % 60:02.0f}m\033[0m ({missing // 60:.0f}h{missing % 60:02.0f}m left ⏳)")

    if args.show_departure:
        # We take the second time_in and the first time_out
        nb_time_in = 0
        first_time_out = 0
        timecheck = None
        for timecheck in t.get_timechecks(today):
            time_in = timecheck["in"]
            time_out = timecheck["out"] or datetime.datetime.now()
            nb_time_in += 1

            # we take the time_out as an int to calculate it
            if timecheck["time_out"] != None and first_time_out == 0:
                first_time_out = 10000*timecheck["out"].hour + 100*timecheck["out"].minute
        if timecheck is not None:
            # we take the time_in as an int to calculate it
            second_time_in = 10000*timecheck["in"].hour + 100*timecheck["in"].minute
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
    hours_balance = datetime.timedelta(hours=balances['hours']['total'])
    print(f"\nbalance of hours before today: {balances['hours']['total']:.1f}h", end="")
    if abs(hours_balance) > datetime.timedelta(hours=10):
        one_day = datetime.timedelta(hours=8)
        print(f" ({hours_balance/one_day:.2} 8-hour days)")
    else:
        print()

    print(f"balance of holidays before today: {balances['holidays']['remaining']}j")

    birthdays = [bd["first_name"] + " " + bd["last_name"] for bd in t.get_birthdays()]
    if len(birthdays) > 0:
        print(f'\n🎂 birthdays: {",".join(birthdays)}')

# vim: set ts=4 sw=4 et:
