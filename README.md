# Cisco sd-wan-cli-mode-converter

This script is used to convert devices from vManage mode to CLI Mode.

User will be prompt to choose from the following options:
```
            [1] Generate list of device in vManage Mode
            [2] Generate list of device in CLI Mode
            [3] Generate running config in .txt for spefic device
            [4] Generate running config in .txt for all deivces
            [5] Convert specific devide to CLI mode
            [6] Convert all devices from vManage Mode to CLI mode
            [7] Exit
```

Use can choose a name for the generated files in options 1, 2, 3. If no name is provided, a timestaped file name will be automatically generated.

# Requirements

To use this code you will need:

* Python 3.7+
* vManage user login details.

# Install and Setup

- Clone the code to local machine.

```
git clone https://github.com/HusseinOmar/cisco-sw-wan-cli-mode-converter.git
cd cisco-sw-wan-cli-mode-converter
```
- Setup Python Virtual Environment (requires Python 3.7+)

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

- Run application file
```
python cli_mode_converter.py 
```

# License
CISCO SAMPLE CODE LICENSE

# Caution
Steps 4 and 6 have sleep timer of 5 second between each iteration. Increase the speel timer accordingly if you have very large number of devices as you can overwhelm vManage.
