# Setup

## Skyline laser

In order to communicate with the laser using a USB port a new driver needs to be installed on the user’s computer. The driver is the Silicon Labs USB to UART bridge. Installation applications for different Windows operating systems are located at Silicon Labs website (https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers, CP210x VCP Driver).

## Yokogawa OSA

The Yokogawa needs to be configured for an Ethernet connection.
The parameters can be accessed through the front panel of your OSA:
-

## Thorlabs power meter

No driver is required. Just connect the device through USB.

## OZOptics attenuator

This device requires the same USB driver as the Skyline.

## Visual Studio code

Open a browser and look for it.

Should be https://code.visualstudio.com

## Python

Run Visual Studio Code, open the side panel "Extensions". Search and install "Python".

## Python packages

### Virtual enviroment

Sometimes Visual Studio Code will not setup your enviroment automatically.
To get the environment ready in VisualCode, run the following commands in your terminal:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
& c:\Users\RomanoC\VS_Code\ALM\.venv\Scripts\Activate.ps1 
.venv\Scripts\activate

Then only you can work!!!!

### Packages

To install python packages (outside the environment):

& c:/Users/RomanoC/VS_Code/ALM/.venv/Scripts/python.exe -m pip install libusb-package PyUSB pyvisa-py pymeasure usb1 openpyxl
& c:/Users/RomanoC/VS_Code/ALM/.venv/Scripts/python.exe -m pip install --upgrade toptica_lasersdk

To install python packages (inside the environment):

pip install libusb-package PyUSB pyvisa-py pymeasure openpyxl
pylablib

### LibUSB

Run the following python code to test the 'libusb-package' package:
import libusb_package

for dev in libusb_package.find(find_all=True):
    print(dev)

# Running the script

There are so far two interesting scripts:
- alm_power_att.py Measures Pout versus Skyline current and attenuation.
- alm_osa_power_att.py Measures Pout and spectrum versus Skyline current and attenuation.

In your virtual environment:
python .\alm_power_att.py -c .\settings_alm_power.json
python .\alm_osa_power_att.py -c settings.json 

Remember to modify the json files to provide the right parameters.

If there are connections problems right at the start of the script, check that you have the right com port or IP address.