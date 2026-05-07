# This code is useful to see if devices are found and what is their ID string

import libusb_package
import usb.core
import pyvisa

# Tell pyvisa-py to use the libusb_package backend
rm = pyvisa.ResourceManager('@py')

# List available instruments
print(rm.list_resources())