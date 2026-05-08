import ctypes
from enum import IntEnum

# --- 1. Enums (must match errors.h and da100_driver.h) ---
class Result(IntEnum):
    OK                      =  0,
    ERR_INVALID_ARG         = -1,
    ERR_NOT_OPEN            = -2,
    ERR_TIMEOUT             = -3,
    ERR_IO                  = -4,
    ERR_PROTOCOL            = -5,
    ERR_CHECKSUM            = -6,
    ERR_BUSY                = -7,
    ERR_BUFFER_FULL         = -8,
    ERR_TRANSPORT           = -9,
    ERR_VERSION             = -10,
    ERR_NOT_IMPLEMENTED     = -11,
    ERR_UNKNOWN             = -99

# --- 2. Structures (must match Device_t in da100_driver.h) ---
class Device(ctypes.Structure):
    _fields_ = [
        ("transport", ctypes.c_void_p),   # TransportHandle_t*
    ]

# --- 3. Load the DLL ---
try:
    from pathlib import Path
    script_dir = Path(__file__).parent.absolute()
    dll_path = script_dir / "da100_driver.dll"
    lib = ctypes.CDLL(str(dll_path))
except OSError as e:
    print(f"Could not load DLL: {e}")
    exit()

# --- 4. Function signatures ---
def _bind(name, argtypes, restype=ctypes.c_int):
    fn = getattr(lib, name)
    fn.argtypes = argtypes
    fn.restype  = restype

_DEV = ctypes.POINTER(Device)
_STR  = ctypes.c_char_p

_bind("Device_Open",                    [_DEV, _STR])
_bind("Device_Close",                   [_DEV])

_bind("Device_GetDeviceNameNVersion",   [_DEV, _STR, _STR, _STR])
_bind("Device_GetSerialNumber",         [_DEV, _STR])

_bind("Device_GetAttenuation",          [_DEV, ctypes.POINTER(ctypes.c_float)])
_bind("Device_SetAttenuation",          [_DEV, ctypes.c_float])

_bind("da100_version",           [], restype=ctypes.c_char_p)
_bind("da100_strerror",          [ctypes.c_int], restype=ctypes.c_char_p)

# --- 5. Helper ---
def _check(res: int):
    """Raises on any non-OK result code."""
    if res != Result.OK:
        msg = lib.da100_strerror(res).decode()
        raise Exception(f"Driver error: {msg} ({Result(res).name})")

# --- 6. High-level wrapper ---
class DA100Device:
    def __init__(self, address: str):
        self._dev     = Device()
        self._address = address.encode("utf-8")

    def __enter__(self):
        _check(lib.Device_Open(ctypes.byref(self._dev), self._address))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        lib.Device_Close(ctypes.byref(self._dev))

    def get_device_name_and_version(self) -> dict:
        name = ctypes.create_string_buffer(32)   # adjust to DA100_NAME_LEN
        sv   = ctypes.create_string_buffer(8)    # adjust to DA100_VERSION_LEN
        hv   = ctypes.create_string_buffer(8)
        _check(lib.Device_GetDeviceNameNVersion(ctypes.byref(self._dev), name, sv, hv))
        return {"name": name.value.decode(), "sw_version": sv.value.decode(), "hw_version": hv.value.decode()}

    def get_serial_number(self) -> str:
        serial = ctypes.create_string_buffer(9)  # adjust to DA100_SERIAL_LEN + 1
        _check(lib.Device_GetSerialNumber(ctypes.byref(self._dev), serial))
        return serial.value.decode()

    def get_attenuation(self) -> float:
        v = ctypes.c_float(); _check(lib.Device_GetAttenuation(ctypes.byref(self._dev), ctypes.byref(v))); return v.value

    def set_attenuation(self, val: float):
        _check(lib.Device_SetAttenuation(ctypes.byref(self._dev), val))

# --- 7. Example usage ---
if __name__ == "__main__":
    import time
    print(f"DA100 Driver v{lib.da100_version().decode()}")

    with DA100Device("COM3:9600:8:N:1") as dev:
        print(f"OZOptics DA100 Driver v{lib.da100_version().decode()}")

        info = dev.get_device_name_and_version()
        print(f"Device name: {info['name']}")
        print(f"Version: {info['sw_version']}, {info['hw_version']}")

        sn = dev.get_serial_number()
        print(f"Serial number: {sn}")

        a = dev.get_attenuation()
        print(f"Attenuation: {a:.6f}")

        step = 5
        for i in range(9):
            dev.set_attenuation(step * i)
            print(f"Device_SetAttenuation: {step * i:.2f} dB")
            time.sleep(10)

        a = dev.get_attenuation()
        print(f"Attenuation: {a:.6f}")
