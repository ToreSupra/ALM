# Requires:
# pip install pylablib

import pylablib as pll
from pylablib.devices import Thorlabs

# List connected Thorlabs devices
devices = Thorlabs.list_kinesis_devices()
print("Found devices:", devices)

# Connect to the motor (serial number from the device label)
motor = Thorlabs.KinesisMotor(devices[0][0])  # Replace with your serial number

# Basic movements
motor.home()                     # Home the motor
motor.move_to(1000)                # Move to position 10
motor.move_by(50000)                 # Move by 5 units
motor.wait_for_stop()            # Wait until motion is complete
print("Scale:", motor.get_scale())
print("Scale units:", motor.get_scale_units())

print("Position:", motor.get_position())

motor.close()