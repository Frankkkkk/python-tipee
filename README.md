# Python Tipee thingy
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

## Dependencies
You need the following env variables set:
- TIPEE_URL (https://xxx.tipee.net)
- TIPEE_USERNAME (foo-bar)
- TIPEE_PASSWORD (secretz)

