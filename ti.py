#!/usr/bin/env python3
"""
Python Tipee thingy

Description:
Display info about tipee timings
frank.villaro@infomaniak.com - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.
"""

# GREEN = 92
# YELLOW = 93
# RED = 91
# BOLD = 1
# ITALIC = 3
# RESET = 0
# Example for green & italic text: `\033[92;3mTEXT\033[0m`

import datetime
import os
import sys
import argparse

import requests
import re

class CustomFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass

nb_hours_per_day = 8

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
        if r.text.strip():  # Tipee likes to reply with a single empty line
            self._cache[url] = r.json()
            return self._cache[url]

    def login(self, username: str, password: str):
        # first we get the CSRF TOKEN
        r = self.session.get(self.instance + "auth/login")
        match = re.search('name="_csrf_token" value="(?P<token>[^"]+)"', r.text)
        if match:
            csrf_token = match.group('token')
        else:
            raise ValueError("Cannot login")
        # then we simulate the login
        payload = {
            "_username": username,
            "_password": password,
            "_csrf_token": csrf_token,
        }
        self.session.post(self.instance + "auth/login", data=payload)
        # and we get our id
        self.id = self._request("brain/users/me")["id"]

    def get_timechecks(self, day=None):
        if not day:
            day = datetime.datetime.now()

        str_day = day.strftime("%Y-%m-%d")

        data = self._request(f"api/employees/{self.id}/workday?date={str_day}")

        for timecheck in data.get("timechecks", []):
            timecheck["in"] = parse_time(timecheck["validation_in"] or timecheck["time_in"] or timecheck["proposal_in"])
            timecheck["out"] = parse_time(timecheck["validation_out"] or timecheck["time_out"] or timecheck["proposal_out"])
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

    parser.add_argument("--no-departure", action="store_false", dest="show_departure", help="Don't show suggested departure time")
    parser.add_argument("-d", "--day", action="store", dest="negative_days", type=int, default=0, help="Display times for a specific day")
    subparsers = parser.add_subparsers(help='Punch your time')
    parser_a = subparsers.add_parser('punch')
    parser_a.add_argument('--punch', default=True)

    return parser.parse_args(args)

def print_header(today, negative_days):
    date_hour_format = today.strftime("%Y-%m-%d")

    if args.negative_days == 0:
        date_hour_format = today.strftime("%Y-%m-%d %H:%M")

    header = f"📅 {negative_days} DAYS AGO {date_hour_format}"
    if negative_days == 0:
        header = f"📅 TODAY {date_hour_format}"
    elif negative_days == 1:
        header = f"📅 YESTERDAY {date_hour_format}"

    print(f"{header}\n" + "-" * (len(header) + 1))

def print_times():

    print(f'Times: ', end='')

    for timecheck in t.get_timechecks(today):

        if timecheck["validation_in"] and (timecheck["validation_in"] != timecheck["time_in"]):
            print(f"\033[91m", end='')
        else:
            print(f"\033[92m", end='')
        print(f'{timecheck["in"].strftime("%H:%M")}\033[0m-', end='')

        if timecheck["out"]:
            if timecheck["validation_out"] and (timecheck["validation_out"] != timecheck["time_out"]):
                print(f"\033[91m", end='')
            else:
                print(f"\033[93m", end='')
            print(f'{timecheck["out"].strftime("%H:%M")}\033[0m', end='')
        else:
            print('…', end='')

        print(' ', end='')

def print_end_of_the_day(missing):
    if args.show_departure:
        # We take the second time_in and the first time_out
        nb_time_in = 0
        first_time_out = 0
        timecheck = None
        for timecheck in t.get_timechecks(today):
            time_in = timecheck["in"]
            time_out = timecheck["out"] or datetime.datetime.now()
            nb_time_in += 1

            # We take the time_out as an int to calculate it
            if timecheck["time_out"] != None and first_time_out == 0:
                first_time_out = 10000*timecheck["out"].hour + 100*timecheck["out"].minute
        if timecheck is not None:
            # We take the time_in as an int to calculate it
            second_time_in = 10000*timecheck["in"].hour + 100*timecheck["in"].minute
            # We remove 30mins if we did not make the break
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
        if (worktime / 60) < nb_hours_per_day:
            print(f"End of the day at: \033[1;93m{hour_end_day}\033[0m 🏃💨")
        else:
            print(f"End of the day at: \033[1;91mNOW GO GO GO\033[0m 🏃💨")

def print_footer():
    balances = t.get_balances()

    hours_balance = datetime.timedelta(hours=balances['hours']['total'])
    hours = int(balances['hours']['total'])
    minutes = balances['hours']['total'] % 1 * 60
    color = '92'
    if hours < 0:
        color = '91'
    print(f"\nBalance of hours before today: \033[{color}m{hours}h{minutes:02.0f}m\033[0m", end="")
    one_day = datetime.timedelta(hours=nb_hours_per_day)
    if abs(hours_balance) > one_day:
        print(f" \033[3m(\033[{color}m{hours_balance/one_day:.3}\033[0m \033[3m{nb_hours_per_day}-hours days)\033[0m")

    holidays = balances['holidays']['remaining']
    color = '92'
    if holidays <= 0:
        color = '93'
    print(f"Balance of holidays before today: \033[{color}m{holidays}j\033[0m")

    birthdays = [bd["first_name"] + " " + bd["last_name"] for bd in t.get_birthdays()]
    if len(birthdays) > 0:
        print(f'\n🎂 Birthdays: {",".join(birthdays)}')


if __name__ == "__main__":
    args = parse_args()

    t = Tipee(os.getenv("TIPEE_URL", default="https://infomaniak.tipee.net/"))
    username = os.getenv("TIPEE_USERNAME")
    password = os.getenv("TIPEE_PASSWORD")
    if username == None or password == None or username == '' or password == '':
        sys.exit("Please set TIPEE_USERNAME and TIPEE_PASSWORD environment variables")
    t.login(username, password)

    today = datetime.datetime.now()
    if args.negative_days != 0:
        delta_days = datetime.timedelta(args.negative_days)
        today = today - delta_days

    print()

    if 'punch' in args:
        t.punch()
        print("The clock has been punched! 🤜⏰\n")

    print_header(today, args.negative_days)

    print_times()

    worktime = t.get_worktime(today).total_seconds() // 60

    when_phrase = "today so far"
    if args.negative_days != 0:
        when_phrase = "that day"
    missing = nb_hours_per_day * 60 - worktime
    print(f"\nTotal worktime {when_phrase}: \033[1m{worktime // 60:.0f}h{worktime % 60:02.0f}m\033[0m", end="")
    if missing < 0:
        missing = abs(missing)
        print(f" \033[3m({missing // 60:.0f}h{missing % 60:02.0f}m over\033[0m ⌛\033[3m)\033[0m")
    else:
        print(f" \033[3m({missing // 60:.0f}h{missing % 60:02.0f}m left\033[0m ⏳\033[3m)\033[0m")

    if args.negative_days == 0:
        print_end_of_the_day(missing)
        print_footer()

    print()

# vim: set ts=4 sw=4 et:
