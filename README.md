# Python Tipee thingy
## Usage
```
$ ./ti.py
📅 TODAY 2021-04-21
-------------------
times: 09:37 12:28 13:24 
total worktime today so far: 6h06m (1h54m left ⏳)
🚪You may leave at 16:01

balance of hours before today: 13h37m
balance of holidays before today: 20j

🎂 birthdays: Alice Bobber
```

You can remove the "you may leave after" message with option `--no-departure`

## Punch your time
```
./ti.py punch
The clock has been punched ! 🤜⏰
📅 TODAY 2021-04-21
-------------------
(...)
```


## Dependencies
You need the following env variables set:
- TIPEE_URL (https://xxx.tipee.net)
- TIPEE_USERNAME (foo-bar)
- TIPEE_PASSWORD (secretz)

