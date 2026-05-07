from toptica.lasersdk.dlcpro.v2_4_0 import DLCpro, SerialConnection
from toptica.lasersdk.utils.dlcpro import *
import time

with DLCpro(SerialConnection('COM4')) as dlc:
    sn = dlc.serial_number.get()
    health = dlc.system_health_txt.get()
    print('Connection established to DLC pro with serial number ' + sn)
    print('System health: ' + health)

    TARGET_WAVELENGTH = 1731.0  # nm
    TOLERANCE = 0.001          # nm
    POLL_INTERVAL = 0.5        # seconds between checks
    TIMEOUT = 30               # seconds before giving up

    dlc.laser1.ctl.wavelength_set.set(TARGET_WAVELENGTH)
    print(f'Wavelength set to {TARGET_WAVELENGTH} nm, waiting...')

    # Wait until actual wavelength is within tolerance
    start_time = time.time()
    while True:
        wavelength = dlc.laser1.ctl.wavelength_act.get()
        print(f'  Current wavelength: {wavelength:.4f} nm')

        if abs(wavelength - TARGET_WAVELENGTH) <= TOLERANCE:
            print(f'Target wavelength reached: {wavelength:.4f} nm')
            break

        if time.time() - start_time > TIMEOUT:
            print(f'Timeout! Final wavelength: {wavelength:.4f} nm')
            break

        time.sleep(POLL_INTERVAL)