import ctypes
from enum import IntEnum

# --- 1. Enums (must match errors.h and skyline_driver.h) ---
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

class InterfaceType(IntEnum):
    RS232           = 0
    USB             = 1
    ETHERNET        = 2

# --- 2. Structures (must match Device_t in skyline_driver.h) ---
class Device(ctypes.Structure):
    _fields_ = [
        ("transport", ctypes.c_void_p),   # TransportHandle_t*
        ("type",      ctypes.c_int),      # InterfaceType_t
    ]

# --- 3. Load the DLL ---
try:
    lib = ctypes.CDLL("./skyline_driver.dll")
except OSError as e:
    print(f"Could not load DLL: {e}")
    exit()

# --- 4. Function signatures ---
def _bind(name, argtypes, restype=ctypes.c_int):
    fn = getattr(lib, name)
    fn.argtypes = argtypes
    fn.restype  = restype

_DEV  = ctypes.POINTER(Device)
_BOOL = ctypes.POINTER(ctypes.c_bool)
_FLT  = ctypes.POINTER(ctypes.c_float)
_INT  = ctypes.POINTER(ctypes.c_int)
_STR  = ctypes.c_char_p

_bind("Device_Open",                         [_DEV, ctypes.c_int, _STR])
_bind("Device_Close",                        [_DEV])
_bind("Device_GetDeviceInfo",                [_DEV, _STR, _STR])
_bind("Device_GetCpldVersion",               [_DEV, _STR])
_bind("Device_Reset",                        [_DEV])
_bind("Device_Save",                         [_DEV])

_bind("Device_IsPump1Enabled",               [_DEV, _BOOL])
_bind("Device_IsPump2Enabled",               [_DEV, _BOOL])
_bind("Device_IsPump3Enabled",               [_DEV, _BOOL])
_bind("Device_SetPump1Enabled",              [_DEV, ctypes.c_bool])
_bind("Device_SetPump2Enabled",              [_DEV, ctypes.c_bool])
_bind("Device_SetPump3Enabled",              [_DEV, ctypes.c_bool])
_bind("Device_GetFeedbackSignals",           [_DEV, _BOOL, _BOOL, _BOOL, _BOOL])
_bind("Device_GetTriggerNLaserStatus",       [_DEV, _BOOL, _BOOL])
_bind("Device_IsSeedTecEnabled",             [_DEV, _BOOL])
_bind("Device_IsPump1TecEnabled",            [_DEV, _BOOL])
_bind("Device_IsPump2TecEnabled",            [_DEV, _BOOL])
_bind("Device_IsPump3TecEnabled",            [_DEV, _BOOL])
_bind("Device_SetSeedTecEnabled",            [_DEV, ctypes.c_bool])
_bind("Device_SetPump1TecEnabled",           [_DEV, ctypes.c_bool])
_bind("Device_SetPump2TecEnabled",           [_DEV, ctypes.c_bool])
_bind("Device_SetPump3TecEnabled",           [_DEV, ctypes.c_bool])

_bind("Device_GetAISeedTemperature",         [_DEV, _FLT])
_bind("Device_GetAIPump1Temperature",        [_DEV, _FLT])
_bind("Device_GetAIPump2Temperature",        [_DEV, _FLT])
_bind("Device_GetAIPump3Temperature",        [_DEV, _FLT])
_bind("Device_GetAIPump1Current",            [_DEV, _FLT])
_bind("Device_GetAIPump2Current",            [_DEV, _FLT])
_bind("Device_GetAIPump3Current",            [_DEV, _FLT])
_bind("Device_GetAIPump1PhPower",            [_DEV, _FLT])
_bind("Device_GetAIPump2PhPower",            [_DEV, _FLT])
_bind("Device_GetAISeedBiasVoltage",         [_DEV, _FLT])
_bind("Device_GetAIAnalogTemperatureSensor1",[_DEV, _FLT])
_bind("Device_GetAIAnalogTemperatureSensor2",[_DEV, _FLT])
_bind("Device_GetAITest5VVoltage",           [_DEV, _BOOL])
_bind("Device_GetAITest1p8VVoltage",         [_DEV, _BOOL])
_bind("Device_GetAITest28VVoltage",          [_DEV, _BOOL])
_bind("Device_GetAIMonitorPhotodiode1",      [_DEV, _FLT])
_bind("Device_GetAIMonitorPhotodiode2",      [_DEV, _FLT])

_bind("Device_GetAOSeedTemperature",         [_DEV, _FLT])
_bind("Device_GetAOPump1Temperature",        [_DEV, _FLT])
_bind("Device_GetAOPump2Temperature",        [_DEV, _FLT])
_bind("Device_GetAOPump3Temperature",        [_DEV, _FLT])
_bind("Device_GetAOSeedCurrent",             [_DEV, _FLT])
_bind("Device_GetAOPump1Current",            [_DEV, _FLT])
_bind("Device_GetAOPump2Current",            [_DEV, _FLT])
_bind("Device_GetAOPump3Current",            [_DEV, _FLT])
_bind("Device_GetAOSeedBiasVoltage",         [_DEV, _FLT])
_bind("Device_SetAOSeedTemperature",         [_DEV, ctypes.c_float])
_bind("Device_SetAOPump1Temperature",        [_DEV, ctypes.c_float])
_bind("Device_SetAOPump2Temperature",        [_DEV, ctypes.c_float])
_bind("Device_SetAOPump3Temperature",        [_DEV, ctypes.c_float])
_bind("Device_SetAOSeedCurrent",             [_DEV, ctypes.c_float])
_bind("Device_SetAOPump1Current",            [_DEV, ctypes.c_float])
_bind("Device_SetAOPump2Current",            [_DEV, ctypes.c_float])
_bind("Device_SetAOPump3Current",            [_DEV, ctypes.c_float])
_bind("Device_SetAOSeedBiasVoltage",         [_DEV, ctypes.c_float])

_bind("Device_GetPumpWriteCurrentLimits",    [_DEV, _FLT, _FLT, _FLT])
_bind("Device_GetTriggerTimeout",            [_DEV, _FLT])
_bind("Device_SetTriggerTimeout",            [_DEV, ctypes.c_float])
_bind("Device_GetPulseWidth",                [_DEV, _INT])
_bind("Device_SetPulseWidth",                [_DEV, ctypes.c_int])
_bind("Device_GetDigitalTemperatureSensor",  [_DEV, _FLT, _FLT])
_bind("Device_GetPulseRepetitionRate",       [_DEV, _FLT])

_bind("Device_GetPumpReadCurrentConstants",  [_DEV, _INT, _INT, _INT])
_bind("Device_SetPump1ReadCurrentConstant",  [_DEV, ctypes.c_int])
_bind("Device_SetPump2ReadCurrentConstant",  [_DEV, ctypes.c_int])
_bind("Device_SetPump3ReadCurrentConstant",  [_DEV, ctypes.c_int])
_bind("Device_GetPumpWriteCurrentConstants", [_DEV, _INT, _INT, _INT])
_bind("Device_SetPump1WriteCurrentConstant", [_DEV, ctypes.c_int])
_bind("Device_SetPump2WriteCurrentConstant", [_DEV, ctypes.c_int])
_bind("Device_SetPump3WriteCurrentConstant", [_DEV, ctypes.c_int])

_bind("skyline_version",                     [], restype=ctypes.c_char_p)
_bind("skyline_strerror",                    [ctypes.c_int], restype=ctypes.c_char_p)

# --- Helper ---
def _check(res: int):
    if res != Result.OK:
        msg = lib.skyline_strerror(res).decode()
        raise Exception(f"Driver error: {msg} ({Result(res).name})")

def _f() -> ctypes.c_float:
    return ctypes.c_float()

def _b() -> ctypes.c_bool:
    return ctypes.c_bool()

def _i() -> ctypes.c_int:
    return ctypes.c_int()

# --- High-level wrapper ---
SERIAL_LEN   = 9   # 8 chars + null
FIRMWARE_LEN = 5   # 4 chars + null
CPLD_LEN     = 5   # 4 chars + null

class SkylineDevice:
    def __init__(self, interface: InterfaceType, address: str):
        self._dev     = Device()
        self._iface   = interface
        self._address = address.encode("utf-8")

    def __enter__(self):
        _check(lib.Device_Open(ctypes.byref(self._dev), self._iface, self._address))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        lib.Device_Close(ctypes.byref(self._dev))

    # -- Device info --
    def get_device_info(self) -> dict:
        serial   = ctypes.create_string_buffer(SERIAL_LEN)
        firmware = ctypes.create_string_buffer(FIRMWARE_LEN)
        _check(lib.Device_GetDeviceInfo(ctypes.byref(self._dev), serial, firmware))
        return {"serial": serial.value.decode(), "firmware": firmware.value.decode()}

    def get_cpld_version(self) -> str:
        cpld = ctypes.create_string_buffer(CPLD_LEN)
        _check(lib.Device_GetCpldVersion(ctypes.byref(self._dev), cpld))
        return cpld.value.decode()

    def reset(self):
        _check(lib.Device_Reset(ctypes.byref(self._dev)))

    def save(self):
        _check(lib.Device_Save(ctypes.byref(self._dev)))

    # -- Pump enable --
    def is_pump1_enabled(self) -> bool:
        v = _b(); _check(lib.Device_IsPump1Enabled(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def is_pump2_enabled(self) -> bool:
        v = _b(); _check(lib.Device_IsPump2Enabled(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def is_pump3_enabled(self) -> bool:
        v = _b(); _check(lib.Device_IsPump3Enabled(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def set_pump1_enabled(self, val: bool): _check(lib.Device_SetPump1Enabled(ctypes.byref(self._dev), val))
    def set_pump2_enabled(self, val: bool): _check(lib.Device_SetPump2Enabled(ctypes.byref(self._dev), val))
    def set_pump3_enabled(self, val: bool): _check(lib.Device_SetPump3Enabled(ctypes.byref(self._dev), val))

    # -- Status --
    def get_feedback_signals(self) -> dict:
        seed, p1, p2, p3 = _b(), _b(), _b(), _b()
        _check(lib.Device_GetFeedbackSignals(ctypes.byref(self._dev),
            ctypes.byref(seed), ctypes.byref(p1), ctypes.byref(p2), ctypes.byref(p3)))
        return {"seed": seed.value, "pump1": p1.value, "pump2": p2.value, "pump3": p3.value}

    def get_trigger_laser_status(self) -> dict:
        trigger, laser = _b(), _b()
        _check(lib.Device_GetTriggerNLaserStatus(ctypes.byref(self._dev),
            ctypes.byref(trigger), ctypes.byref(laser)))
        return {"trigger": trigger.value, "laser": laser.value}

    # -- TEC enable --
    def is_seed_tec_enabled(self) -> bool:
        v = _b(); _check(lib.Device_IsSeedTecEnabled(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def is_pump1_tec_enabled(self) -> bool:
        v = _b(); _check(lib.Device_IsPump1TecEnabled(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def is_pump2_tec_enabled(self) -> bool:
        v = _b(); _check(lib.Device_IsPump2TecEnabled(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def is_pump3_tec_enabled(self) -> bool:
        v = _b(); _check(lib.Device_IsPump3TecEnabled(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def set_seed_tec_enabled(self, val: bool):  _check(lib.Device_SetSeedTecEnabled (ctypes.byref(self._dev), val))
    def set_pump1_tec_enabled(self, val: bool): _check(lib.Device_SetPump1TecEnabled(ctypes.byref(self._dev), val))
    def set_pump2_tec_enabled(self, val: bool): _check(lib.Device_SetPump2TecEnabled(ctypes.byref(self._dev), val))
    def set_pump3_tec_enabled(self, val: bool): _check(lib.Device_SetPump3TecEnabled(ctypes.byref(self._dev), val))

    # -- Analog inputs --
    def get_ai_seed_temperature(self) -> float:
        v = _f(); _check(lib.Device_GetAISeedTemperature(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_pump1_temperature(self) -> float:
        v = _f(); _check(lib.Device_GetAIPump1Temperature(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_pump2_temperature(self) -> float:
        v = _f(); _check(lib.Device_GetAIPump2Temperature(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_pump3_temperature(self) -> float:
        v = _f(); _check(lib.Device_GetAIPump3Temperature(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_pump1_current(self) -> float:
        v = _f(); _check(lib.Device_GetAIPump1Current(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_pump2_current(self) -> float:
        v = _f(); _check(lib.Device_GetAIPump2Current(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_pump3_current(self) -> float:
        v = _f(); _check(lib.Device_GetAIPump3Current(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_pump1_ph_power(self) -> float:
        v = _f(); _check(lib.Device_GetAIPump1PhPower(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_pump2_ph_power(self) -> float:
        v = _f(); _check(lib.Device_GetAIPump2PhPower(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_seed_bias_voltage(self) -> float:
        v = _f(); _check(lib.Device_GetAISeedBiasVoltage(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_analog_temperature_sensor1(self) -> float:
        v = _f(); _check(lib.Device_GetAIAnalogTemperatureSensor1(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_analog_temperature_sensor2(self) -> float:
        v = _f(); _check(lib.Device_GetAIAnalogTemperatureSensor2(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_test_5v(self) -> bool:
        v = _b(); _check(lib.Device_GetAITest5VVoltage(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_test_1p8v(self) -> bool:
        v = _b(); _check(lib.Device_GetAITest1p8VVoltage(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_test_28v(self) -> bool:
        v = _b(); _check(lib.Device_GetAITest28VVoltage(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_monitor_photodiode1(self) -> float:
        v = _f(); _check(lib.Device_GetAIMonitorPhotodiode1(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ai_monitor_photodiode2(self) -> float:
        v = _f(); _check(lib.Device_GetAIMonitorPhotodiode2(ctypes.byref(self._dev), ctypes.byref(v))); return v.value

    # -- Analog outputs (get) --
    def get_ao_seed_temperature(self) -> float:
        v = _f(); _check(lib.Device_GetAOSeedTemperature(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ao_pump1_temperature(self) -> float:
        v = _f(); _check(lib.Device_GetAOPump1Temperature(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ao_pump2_temperature(self) -> float:
        v = _f(); _check(lib.Device_GetAOPump2Temperature(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ao_pump3_temperature(self) -> float:
        v = _f(); _check(lib.Device_GetAOPump3Temperature(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ao_seed_current(self) -> float:
        v = _f(); _check(lib.Device_GetAOSeedCurrent(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ao_pump1_current(self) -> float:
        v = _f(); _check(lib.Device_GetAOPump1Current(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ao_pump2_current(self) -> float:
        v = _f(); _check(lib.Device_GetAOPump2Current(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ao_pump3_current(self) -> float:
        v = _f(); _check(lib.Device_GetAOPump3Current(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def get_ao_seed_bias_voltage(self) -> float:
        v = _f(); _check(lib.Device_GetAOSeedBiasVoltage(ctypes.byref(self._dev), ctypes.byref(v))); return v.value

    # -- Analog outputs (set) --
    def set_ao_seed_temperature(self, temp: float):    _check(lib.Device_SetAOSeedTemperature (ctypes.byref(self._dev), temp))
    def set_ao_pump1_temperature(self, temp: float):   _check(lib.Device_SetAOPump1Temperature(ctypes.byref(self._dev), temp))
    def set_ao_pump2_temperature(self, temp: float):   _check(lib.Device_SetAOPump2Temperature(ctypes.byref(self._dev), temp))
    def set_ao_pump3_temperature(self, temp: float):   _check(lib.Device_SetAOPump3Temperature(ctypes.byref(self._dev), temp))
    def set_ao_seed_current(self, current: float):     _check(lib.Device_SetAOSeedCurrent     (ctypes.byref(self._dev), current))
    def set_ao_pump1_current(self, current: float):    _check(lib.Device_SetAOPump1Current    (ctypes.byref(self._dev), current))
    def set_ao_pump2_current(self, current: float):    _check(lib.Device_SetAOPump2Current    (ctypes.byref(self._dev), current))
    def set_ao_pump3_current(self, current: float):    _check(lib.Device_SetAOPump3Current    (ctypes.byref(self._dev), current))
    def set_ao_seed_bias_voltage(self, voltage: float):_check(lib.Device_SetAOSeedBiasVoltage (ctypes.byref(self._dev), voltage))

    # -- Pump current limits --
    def get_pump_write_current_limits(self) -> dict:
        c1, c2, c3 = _f(), _f(), _f()
        _check(lib.Device_GetPumpWriteCurrentLimits(ctypes.byref(self._dev),
            ctypes.byref(c1), ctypes.byref(c2), ctypes.byref(c3)))
        return {"pump1": c1.value, "pump2": c2.value, "pump3": c3.value}

    # -- Trigger / pulse --
    def get_trigger_timeout(self) -> float:
        v = _f(); _check(lib.Device_GetTriggerTimeout(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def set_trigger_timeout(self, freq: float):
        _check(lib.Device_SetTriggerTimeout(ctypes.byref(self._dev), freq))

    def get_pulse_width(self) -> int:
        v = _i(); _check(lib.Device_GetPulseWidth(ctypes.byref(self._dev), ctypes.byref(v))); return v.value
    def set_pulse_width(self, pw: int):
        _check(lib.Device_SetPulseWidth(ctypes.byref(self._dev), pw))

    def get_pulse_repetition_rate(self) -> float:
        v = _f(); _check(lib.Device_GetPulseRepetitionRate(ctypes.byref(self._dev), ctypes.byref(v))); return v.value

    def get_digital_temperature_sensor(self) -> dict:
        t1, t2 = _f(), _f()
        _check(lib.Device_GetDigitalTemperatureSensor(ctypes.byref(self._dev),
            ctypes.byref(t1), ctypes.byref(t2)))
        return {"t1": t1.value, "t2": t2.value}

    # -- Current constants --
    def get_pump_read_current_constants(self) -> dict:
        c1, c2, c3 = _i(), _i(), _i()
        _check(lib.Device_GetPumpReadCurrentConstants(ctypes.byref(self._dev),
            ctypes.byref(c1), ctypes.byref(c2), ctypes.byref(c3)))
        return {"pump1": c1.value, "pump2": c2.value, "pump3": c3.value}

    def set_pump1_read_current_constant(self, val: int): _check(lib.Device_SetPump1ReadCurrentConstant(ctypes.byref(self._dev), val))
    def set_pump2_read_current_constant(self, val: int): _check(lib.Device_SetPump2ReadCurrentConstant(ctypes.byref(self._dev), val))
    def set_pump3_read_current_constant(self, val: int): _check(lib.Device_SetPump3ReadCurrentConstant(ctypes.byref(self._dev), val))

    def get_pump_write_current_constants(self) -> dict:
        c1, c2, c3 = _i(), _i(), _i()
        _check(lib.Device_GetPumpWriteCurrentConstants(ctypes.byref(self._dev),
            ctypes.byref(c1), ctypes.byref(c2), ctypes.byref(c3)))
        return {"pump1": c1.value, "pump2": c2.value, "pump3": c3.value}

    def set_pump1_write_current_constant(self, val: int): _check(lib.Device_SetPump1WriteCurrentConstant(ctypes.byref(self._dev), val))
    def set_pump2_write_current_constant(self, val: int): _check(lib.Device_SetPump2WriteCurrentConstant(ctypes.byref(self._dev), val))
    def set_pump3_write_current_constant(self, val: int): _check(lib.Device_SetPump3WriteCurrentConstant(ctypes.byref(self._dev), val))


# --- Example usage ---
if __name__ == "__main__":
    print(f"Skyline Driver v{lib.skyline_version().decode()}")

    with SkylineDevice(InterfaceType.RS232, "COM3:57600:8:N:1") as dev:
        # --- Device info ---
        print("\n--- Device Info ---")
        info = dev.get_device_info()
        print(f"  Serial:   {info['serial']}")
        print(f"  Firmware: {info['firmware']}")
        print(f"  CPLD:     {dev.get_cpld_version()}")

        # --- Trigger / Pulse ---
        print("\n--- Trigger / Pulse ---")
        print(f"  Trigger timeout:       {dev.get_trigger_timeout()} s")
        print(f"  Pulse width:           {dev.get_pulse_width()} us")
        print(f"  Pulse repetition rate: {dev.get_pulse_repetition_rate()} Hz")
        print(f"  Trigger/Laser status:  {dev.get_trigger_laser_status()}")

        # --- Digital temperature sensors ---
        print("\n--- Digital Temperature Sensors ---")
        dts = dev.get_digital_temperature_sensor()
        print(f"  T1: {dts['t1']:.2f} °C")
        print(f"  T2: {dts['t2']:.2f} °C")

        # --- Analog inputs (read-only telemetry) ---
        print("\n--- Analog Inputs ---")
        print(f"  Seed temperature:          {dev.get_ai_seed_temperature():.2f} °C")
        print(f"  Pump1 temperature:         {dev.get_ai_pump1_temperature():.2f} °C")
        print(f"  Pump2 temperature:         {dev.get_ai_pump2_temperature():.2f} °C")
        print(f"  Pump3 temperature:         {dev.get_ai_pump3_temperature():.2f} °C")
        print(f"  Pump1 current:             {dev.get_ai_pump1_current():.4f} A")
        print(f"  Pump2 current:             {dev.get_ai_pump2_current():.4f} A")
        print(f"  Pump3 current:             {dev.get_ai_pump3_current():.4f} A")
        print(f"  Pump1 Ph power:            {dev.get_ai_pump1_ph_power():.4f} W")
        print(f"  Pump2 Ph power:            {dev.get_ai_pump2_ph_power():.4f} W")
        print(f"  Seed bias voltage:         {dev.get_ai_seed_bias_voltage():.4f} V")
        print(f"  Analog temp sensor 1:      {dev.get_ai_analog_temperature_sensor1():.2f} °C")
        print(f"  Analog temp sensor 2:      {dev.get_ai_analog_temperature_sensor2():.2f} °C")
        print(f"  Monitor photodiode 1:      {dev.get_ai_monitor_photodiode1():.4f}")
        print(f"  Monitor photodiode 2:      {dev.get_ai_monitor_photodiode2():.4f}")
        print(f"  Test 5V rail OK:           {dev.get_ai_test_5v()}")
        print(f"  Test 1.8V rail OK:         {dev.get_ai_test_1p8v()}")
        print(f"  Test 28V rail OK:          {dev.get_ai_test_28v()}")

        # --- Feedback & status ---
        print("\n--- Feedback Signals ---")
        fb = dev.get_feedback_signals()
        print(f"  Seed:  {fb['seed']}")
        print(f"  Pump1: {fb['pump1']}")
        print(f"  Pump2: {fb['pump2']}")
        print(f"  Pump3: {fb['pump3']}")

        # --- Pump enable state ---
        print("\n--- Pump Enable State ---")
        print(f"  Pump1 enabled: {dev.is_pump1_enabled()}")
        print(f"  Pump2 enabled: {dev.is_pump2_enabled()}")
        print(f"  Pump3 enabled: {dev.is_pump3_enabled()}")

        # --- TEC enable state ---
        print("\n--- TEC Enable State ---")
        print(f"  Seed TEC enabled:  {dev.is_seed_tec_enabled()}")
        print(f"  Pump1 TEC enabled: {dev.is_pump1_tec_enabled()}")
        print(f"  Pump2 TEC enabled: {dev.is_pump2_tec_enabled()}")
        print(f"  Pump3 TEC enabled: {dev.is_pump3_tec_enabled()}")

        # --- Analog outputs (current setpoints) ---
        print("\n--- Analog Output Setpoints ---")
        print(f"  Seed temperature SP:   {dev.get_ao_seed_temperature():.2f} °C")
        print(f"  Pump1 temperature SP:  {dev.get_ao_pump1_temperature():.2f} °C")
        print(f"  Pump2 temperature SP:  {dev.get_ao_pump2_temperature():.2f} °C")
        print(f"  Pump3 temperature SP:  {dev.get_ao_pump3_temperature():.2f} °C")
        print(f"  Seed current SP:       {dev.get_ao_seed_current():.4f} A")
        print(f"  Pump1 current SP:      {dev.get_ao_pump1_current():.4f} A")
        print(f"  Pump2 current SP:      {dev.get_ao_pump2_current():.4f} A")
        print(f"  Pump3 current SP:      {dev.get_ao_pump3_current():.4f} A")
        print(f"  Seed bias voltage SP:  {dev.get_ao_seed_bias_voltage():.4f} V")

        # --- Current limits ---
        print("\n--- Pump Write Current Limits ---")
        limits = dev.get_pump_write_current_limits()
        print(f"  Pump1 limit: {limits['pump1']:.4f} A")
        print(f"  Pump2 limit: {limits['pump2']:.4f} A")
        print(f"  Pump3 limit: {limits['pump3']:.4f} A")

        # --- Current calibration constants ---
        print("\n--- Pump Read Current Constants ---")
        rc = dev.get_pump_read_current_constants()
        print(f"  Pump1: {rc['pump1']}")
        print(f"  Pump2: {rc['pump2']}")
        print(f"  Pump3: {rc['pump3']}")

        print("\n--- Pump Write Current Constants ---")
        wc = dev.get_pump_write_current_constants()
        print(f"  Pump1: {wc['pump1']}")
        print(f"  Pump2: {wc['pump2']}")
        print(f"  Pump3: {wc['pump3']}")

        print("\n--- Done ---")
