# Python Tipee thingy

## Installation

### python-dotenv

This script also uses the lib `python-dotenv` to load environment variables from the `.env` file.

This installation is not mandatory but you should put your environment variables in a root configuration file like `.bashrc` or `.zshrc`.

So please install it too if you want use `.env` file:
```
$ pip install python-dotenv
```
More information about python-dotenv [here](https://pypi.org/project/python-dotenv/)
### python-dotenv
#### ⚠️ Not mandatory for the proper functioning of the script without journey.
This script Tipee use the library `Tabulate` for create the table of routes in public transport. So if you want to have this route, please install it. (More information about tabulate [here](https://github.com/astanin/python-tabulate))
```
pip install tabulate
```

## Usage
```
$ ./ti.py
📅 TODAY 2021-07-07
-------------------
times: 08:54 
total worktime today so far: 2h55m (5h05m left ⏳)
End of the day at: 17h24m 🏃💨

balance of hours before today: 19h56m
balance of holidays before today: 9.82j

🎂 birthdays: Alice Bobber
```

ℹ️ You can remove the "you may leave after" message with option `--no-departure`. The End of day add 30mins if you don't do your break.

## Punch your time
```
./ti.py --punch
The clock has been punched ! 🤜⏰
📅 TODAY 2021-07-07
-------------------
(...)
```

## Get the weather of your city
We show you the current weather at home.
```
./ti.py --weather
(...)
Weather report: geneva

   _`/"".-.     Light rain shower, thunderstorm in vicinity, rain with thunderstorm
    ,\_(   ).   19 °C
     /(___(__)  ↑ 15 km/h
       ‘ ‘ ‘ ‘  10 km
      ‘ ‘ ‘ ‘   0.0 mm
(...)
```

## Have your journey from work to home
We also show you the public transport route from your work to your home! You just have to fill in the environment variable `TIPEE_FROM` so that we can know in which city and street you work. <br>
Works with all cities and streets in Switzerland, but only works with some cities and streets around Switzerland.
```
./ti.py --route
(...)
                        ====================================================================================
                        |   Carouge GE, Pictet-Thellusson   |   <---01h12m--->   |   Lausanne, Georgette   |
                        ====================================================================================
╒════╤═══════════════╤═══════════════════════╤═════════════╤═══════════════════════════════╤════════╤═════════════════════╤════════╕
│    │ Transport     │ Line                  │ Platform    │ Departure                     │ HD     │ Arrival             │ HA     │
╞════╪═══════════════╪═══════════════════════╪═════════════╪═══════════════════════════════╪════════╪═════════════════════╪════════╡
│  1 │ |  ➡️    🚊  | │ 15 -> Genève, Nations │ No platform │ Carouge GE, Pictet-Thellusson │ 14h20m │ Genève, Cornavin    │ 14h34m │
├────┼───────────────┼───────────────────────┼─────────────┼───────────────────────────────┼────────┼─────────────────────┼────────┤
│  2 │ |  ➡️    🚶  | │ N/A                   │ No platform │ Genève, Cornavin              │ 14h34m │ Genève              │ 14h39m │
├────┼───────────────┼───────────────────────┼─────────────┼───────────────────────────────┼────────┼─────────────────────┼────────┤
│  3 │ |  ➡️    🚆  | │ IC1 -> St. Gallen     │ Plaform N°6 │ Genève                        │ 14h42m │ Lausanne            │ 15h18m │
├────┼───────────────┼───────────────────────┼─────────────┼───────────────────────────────┼────────┼─────────────────────┼────────┤
│  4 │ |  ➡️    🚶  | │ N/A                   │ No platform │ Lausanne                      │ 15h18m │ Lausanne, Closelet  │ 15h23m │
├────┼───────────────┼───────────────────────┼─────────────┼───────────────────────────────┼────────┼─────────────────────┼────────┤
│  5 │ |  ➡️    🚌  | │ 2 -> Lausanne, Désert │ No platform │ Lausanne, Closelet            │ 15h29m │ Lausanne, Georgette │ 15h32m │
╘════╧═══════════════╧═══════════════════════╧═════════════╧═══════════════════════════════╧════════╧═════════════════════╧════════╛
(...)
```

## Dependencies
You need the following env variables set:
- TIPEE_URL (https://xxx.tipee.net)
- TIPEE_USERNAME (foo-bar)
- TIPEE_PASSWORD (secretz)
- TIPEE_FROM (City, street)

You can put them in the `.env` file (renaming the `.env.example`).

Or put them in a root configuration file like `.bashrc` or `.zshrc`.