#!/usr/bin/env python3
"""
Python Tipee thingy

Description:
Display info about tipee timings
frank.villaro@infomaniak.com - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.
"""
from dotenv import load_dotenv
import datetime
import os
import sys
import argparse
import re
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
        r.raise_for_status()

        self._get_me()

    def _get_me(self):
        url = self.instance + "brain/users/me"
        r = self.session.get(url)
        self.id = r.json()["id"]
        address_user = r.json()["address"]
        city_user = r.json()["city"]
        if address_user == None :
            address_user = os.getenv("TIPEE_TO")
            if address_user != None:
                city_user = address_user.split(',')[0]

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

    def print_timechecks(timechecks):
        for timecheck in timechecks:
            for field in ["time_in", "time_out", "proposal_in", "proposal_out"]:
                dt = parse_time(timecheck[field], None)
                if dt == None:
                    pass
                elif field in ["proposal_out"] or field in ["proposal_in"]:
                    print(f'\033[93m{dt.strftime("%H:%M")}\033[0m ', end="")
                elif dt is not None:
                    print(f'\033[92m{dt.strftime("%H:%M")}\033[0m ', end="")

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
            if timecheck["time_in"] == None:
                time_in = parse_time(timecheck["proposal_in"])
            elif timecheck["time_out"] == None:
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

class Route:
    def get_title():
        departure_global_name = jsontext['connections'][0]['from']['station']['name']
        arrival_global_name = jsontext['connections'][0]['to']['station']['name']
        duration = "{:%Hh%Mm}".format(datetime.datetime.strptime(jsontext['connections'][0]['duration'], "00d%H:%M:%S"))

        title_only = f"|   {departure_global_name}   |   <---\033[92m{duration}\033[0m--->   |   {arrival_global_name}   |"
        title_length = "=" * (len(title_only) - 9)
        table_size = len(tableau.splitlines()[0])
        title_size = (len(title_only) - 9)

        if (table_size % 2) == 0 and (title_size % 2) != 0:
            title = f"{title_length.center(table_size)}\n{title_only.center(table_size + 8)}\n{title_length.center(table_size)}"
        elif (table_size % 2) != 0 and (title_size % 2) == 0:
            title = f"{title_length.center(table_size)}\n{title_only.center(table_size + 10)}\n{title_length.center(table_size)}"
        else:
            title = f"{title_length.center(table_size)}\n{title_only.center(table_size + 9)}\n{title_length.center(table_size)}"

        return title, title_only
    def get_line():
        if jsontext['connections'][0]['sections'][nb_section]['walk'] != None:
            category = "N/A"
            number = ""
            to_route = ""
        elif jsontext['connections'][0]['sections'][nb_section]['journey']['category'] in transport_dict:
            category = ""
            number = jsontext['connections'][0]['sections'][nb_section]['journey']['number'] + " -> "
            to_route = jsontext['connections'][0]['sections'][nb_section]['journey']['to']
        else:
            category = jsontext['connections'][0]['sections'][nb_section]['journey']['category']
            number = jsontext['connections'][0]['sections'][nb_section]['journey']['number'] + " -> "
            to_route = jsontext['connections'][0]['sections'][nb_section]['journey']['to']

        return category, number, to_route

    def get_transport():

        if jsontext['connections'][0]['sections'][nb_section]['walk'] != None:
            transport = "|  ➡️    🚶  |"
        elif jsontext['connections'][0]['sections'][nb_section]['journey']['category'] in train:
            transport = "|  ➡️    🚆  |"
        elif jsontext['connections'][0]['sections'][nb_section]['journey']['category'] in transport_dict:
            transport = transport_dict[jsontext['connections'][0]['sections'][nb_section]['journey']['category']]
        else:
            transport = "N/A"

        return transport

    def get_platform():
        if jsontext['connections'][0]['sections'][nb_section]['walk'] != None or jsontext['connections'][0]['sections'][nb_section]['journey']['passList'][0]['platform'] == None:
            platform = "No platform"
        else:
            platform = "Plaform N°" + jsontext['connections'][0]['sections'][nb_section]['journey']['passList'][0]['platform']

        return platform

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
    parser.add_argument('-hi', '--history', action='store_true', help="Displays the punch of the last 7 days")
    parser.add_argument('-d', '--no-departure', dest="no_departure", action='store_true', help="don't show you what time you can leave")
    parser.add_argument('-w', '--weather', action='store_true', help="show the current weather")
    parser.add_argument('-r', '--route', action='store_true', help="show your route with pulic transport")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    # load the environement variable in .env file
    load_dotenv()

    t = Tipee(os.getenv("TIPEE_URL", default="https://infomaniak.tipee.net/"))
    username = os.getenv("TIPEE_USERNAME")
    password = os.getenv("TIPEE_PASSWORD")
    if username == None or password == None or username == '' or password == '':
        sys.exit("Please set TIPEE_USERNAME and TIPEE_PASSWORD environment variables")
    t.login(username, password)

    today = datetime.datetime.now()

    if args.history:
        for i in reversed(range(7)):
            day = datetime.date.today() - datetime.timedelta(days=i)
            print(f"{day} : ", end="")
            time_checks = t.get_timechecks(day)
            if time_checks != []:
                Tipee.print_timechecks(time_checks)
            else:
                print("\033[31mNo timechecks for this day\033[0m", end="")  
            print("\n")
        exit(1)

    if args.punch:
        t.punch()
        print("The clock has been punched ! 🤜⏰")

    print(f'📅 TODAY {today.strftime("%Y-%m-%d")}\n-------------------\ntimes: ', end="")
    Tipee.print_timechecks(t.get_timechecks(today))
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
            if timecheck["time_in"] == None:
                time_in = parse_time(timecheck["proposal_in"])
            elif timecheck["time_out"] == None:
                time_out = parse_time(timecheck["proposal_out"], datetime.datetime.now())
            nb_time_in += 1

            # we take the time_out as an int to calculate it
            if timecheck["time_out"] != None:
                first_time_out = 10000*datetime.datetime.strptime(str(time_out), "%Y-%m-%d %H:%M:%S").hour + 100*datetime.datetime.strptime(str(time_out), "%Y-%m-%d %H:%M:%S").minute
        # we take the time_in as an int to calculate it
        second_time_in = 10000*datetime.datetime.strptime(str(time_in), "%Y-%m-%d %H:%M:%S").hour + 100*datetime.datetime.strptime(str(time_in), "%Y-%m-%d %H:%M:%S").minute
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

    # Routes
    if args.route:

        # try to import the tabulate module. We import this module at the middle of the script beacause it is not mandatory for the proper functioning of the script without journey
        try:
            from tabulate import tabulate
        except ImportError or ModuleNotFoundError:
            # The tabulate module does not exist, display proper error message and exit
            print('\n⚠️  \033[93mYour route in public transport can only run with tabulate module.\033[0m \n   --> So please install TABULATE with "\033[1mpip install tabulate\033[0m".')
            sys.exit(1)

        # We set the environment variables
        from_name = os.getenv("TIPEE_FROM")
        to_name, city_user = t._get_me()                 # with a environement variable : os.getenv("TIPEE_TO")


        if from_name is None or to_name is None:
            print("\nℹ️  Please set TIPEE_FROM environment variable to get your journey by public transport\n")

        else:
            # Variable formatting
            from_name = from_name.replace(",", "%2C")
            from_name = from_name.replace(" ", "+")

            to_name = to_name.replace(",", "%2C")
            to_name = to_name.replace(" ", "+")

            date_route_now = str(datetime.datetime.now() + datetime.timedelta(minutes=5))
            date_route = "{:%Y-%m-%dT%H}".format(datetime.datetime.strptime(date_route_now, "%Y-%m-%d %H:%M:%S.%f")) + "%3A" + "{:%M}".format(datetime.datetime.strptime(date_route_now, "%Y-%m-%d %H:%M:%S.%f"))

            # API transport
            urlCFF = f"http://transport.opendata.ch/v1/connections?from={from_name}&to={to_name}&datetime={date_route}"

            responseCFF = requests.get(urlCFF)        # To execute get request
            jsontext = responseCFF.json()

            # Try to get information from the Transport json and if there is an error, it prints an error message
            try:
                error_test = jsontext['connections'][0]['sections']
            except IndexError:
                print('⚠️  \033[93mOuuups it is not possible to make an itinerary with the departure you have entered or the arrival associated with your Tipee account.\033[0m \n   --> Please try to change the "\033[1mTIPEE_FROM\033[0m" environement variable and try again')
                sys.exit(1)

            nb_section = -1
            nb_steps_route = 1

            # Empty table
            route = {"Transport":[], "Line":[], "Platform":[], "Departure":[], "HD":[], "Arrival":[], "HA":[]}

            # Every train
            train = ["AG", "ARC", "ARZ", "AT", "ATR", "ATZ", "AVE", "BEX", "CAT", "CNL", "D", "E", "EC", "EM", "EN", "ES", "EST", "EXT", "GEX", "IC", "ICE", "ICN", "IN", "IR", "IRE", "IT", "JAT", "MAT", "MP", "NJ", "NZ", "P", "PE", "R", "RB", "RE", "RJ", "RJX", "S", "SN", "STB", "TAL", "TER", "TE2", "TGV", "THA", "TLK", "UEX", "VAE", "WB", "X", "X2", "ZUG"]

            transport_dict = {"T":"|  ➡️    🚊  |", "M":"|  ➡️    🚇  |", "B": "|  ➡️    🚌  |", "BAT":"|  ➡️    🚢  |"}

            for jsontext['journey'] in jsontext['connections'][0]['sections']:
                # Set the variables
                nb_section += 1
                nb_steps_route += 1

                # departure / arrival
                departure = jsontext['connections'][0]['sections'][nb_section]['departure']['station']['name']
                arrival = jsontext['connections'][0]['sections'][nb_section]['arrival']['station']['name']

                #Houre
                departure_time = '{:%Hh%Mm}'.format(datetime.datetime.strptime(jsontext['connections'][0]['sections'][nb_section]['departure']['departure'], '%Y-%m-%dT%H:%M:%S+%f'))
                arrival_time = '{:%Hh%Mm}'.format(datetime.datetime.strptime(jsontext['connections'][0]['sections'][nb_section]['arrival']['arrival'], '%Y-%m-%dT%H:%M:%S+%f'))

                # Transport
                transport = Route.get_transport()

                #Line
                category, number, to_route = Route.get_line()

                # Plateform
                platform = Route.get_platform()

                # Construction of the list for the table
                route["Transport"].append(transport)
                route["Line"].append(category + number + to_route)
                route["Platform"].append(platform)
                route["Departure"].append(departure)
                route["HD"].append(departure_time)
                route["Arrival"].append(arrival)
                route["HA"].append(arrival_time)

            # we print the route table
            tableau = tabulate(route, headers='keys', tablefmt='fancy_grid', showindex=range(1,nb_steps_route))

            # Title of the route
            title, title_only = Route.get_title()

            print(title)
            print(tableau)
    else:
        pass

# vim: set ts=4 sw=4 et:
