# This file is testing that the package is working well.
# It was crashing because the libusb-1.0.dll was not installed in the right folder.
# I had to copy it:
# copy .venv\Lib\site-packages\usb1\libusb-1.0.dll .venv\Lib\site-packages\libusb_package\

import libusb_package

for dev in libusb_package.find(find_all=True):
    print(dev)