from toptica.lasersdk.dlcpro.v2_4_0 import DLCpro, SerialConnection
from toptica.lasersdk.utils.dlcpro import *
import time
import numpy as np

from pymeasure.instruments.thorlabs import ThorlabsPM100USB

WAVELENGTH_MIN = 1620
WAVELENGTH_MAX = 1750
WAVELENGTH_STEP = 5

from Tests.TestFindThorlabs import find_thorlabs_pm100

devices = find_thorlabs_pm100()

if not devices:
    print("No Thorlabs PM100-series device found.")
elif len(devices) > 1:
    print("not right")
else:
    pm = ThorlabsPM100USB(devices[0]["resource_string"])

with DLCpro(SerialConnection('COM8')) as dlc:
    sn = dlc.serial_number.get()
    health = dlc.system_health_txt.get()
    print('Connection established to DLC pro with serial number ' + sn)
    print('System health: ' + health)

    TOLERANCE = 0.001          # nm
    POLL_INTERVAL = 0.5        # seconds between checks
    TIMEOUT = 30               # seconds before giving up

    print(f"Wavelength [nm], Power [mW]")
    for TARGET_WAVELENGTH in np.arange(WAVELENGTH_MIN, WAVELENGTH_MAX+WAVELENGTH_STEP, WAVELENGTH_STEP):
        dlc.laser1.ctl.wavelength_set.set(float(TARGET_WAVELENGTH))

        # Wait until actual wavelength is within tolerance
        start_time = time.time()
        while True:
            wavelength = dlc.laser1.ctl.wavelength_act.get()

            if abs(wavelength - TARGET_WAVELENGTH) <= TOLERANCE:
                break

            if time.time() - start_time > TIMEOUT:
                break

            time.sleep(POLL_INTERVAL)

        pm.wavelength = TARGET_WAVELENGTH
        time.sleep(5)
        power = pm.power
        print(f"{pm.wavelength}, {power * 1e3:.6f}")
    
    pm.shutdown()