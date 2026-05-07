import usb.core
import usb.backend.libusb1
import os

# --- Config ---
THORLABS_VENDOR_ID = 0x1313
PM100_PRODUCT_IDS  = {
    0x8078: "PM100USB",
    0x8072: "PM100D",
    0x807B: "PM200",
    0x8079: "PM400",
}

def get_libusb_backend():
    """
    Try to find libusb-1.0 backend automatically.
    First tries default system paths, then falls back to the venv usb1 folder.
    """
    # 1. Try default system search first
    backend = usb.backend.libusb1.get_backend()
    if backend is not None:
        print("Backend found via system path.")
        return backend

    # 2. Fall back: look in venv's usb1 folder (where libusb1 package puts the DLL)
    usb1_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..','.venv', 'Lib', 'site-packages', 'usb1', 'libusb-1.0.dll'
    )
    if os.path.exists(usb1_path):
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: usb1_path)
        if backend is not None:
            print("Backend found in venv usb1 folder.")
            return backend

    raise RuntimeError("No libusb backend found. Check your libusb1 installation.")

def find_thorlabs_pm100():
    """
    Scans USB devices and returns a list of dicts for every
    Thorlabs PM100-series instrument found.
    Each dict contains: model, serial, resource_string.
    Returns an empty list if no device is found.
    """
    backend = get_libusb_backend()
    devices = usb.core.find(find_all=True, backend=backend, idVendor=THORLABS_VENDOR_ID)

    found = []
    for dev in devices:
        pid = dev.idProduct
        if pid in PM100_PRODUCT_IDS:
            try:
                serial = usb.util.get_string(dev, dev.iSerialNumber)
            except Exception:
                serial = "UNKNOWN"

            entry = {
                "model"           : PM100_PRODUCT_IDS[pid],
                "serial"          : serial,
                "vendor_id"       : THORLABS_VENDOR_ID,
                "product_id"      : pid,
                "resource_string" : f"USB0::0x{THORLABS_VENDOR_ID:04X}::0x{pid:04X}::{serial}::INSTR",
            }
            found.append(entry)

    return found


# --- Main ---
if __name__ == "__main__":
    from pymeasure.instruments.thorlabs import ThorlabsPM100USB

    devices = find_thorlabs_pm100()

    if not devices:
        print("No Thorlabs PM100-series device found.")
    else:
        print(f"Found {len(devices)} device(s):\n")
        for i, d in enumerate(devices):
            print(f"  [{i}] {d['model']}  SN: {d['serial']}  VISA: {d['resource_string']}")

        print()

        # Connect to all found devices and read power
        for d in devices:
            print(f"--- {d['model']} | SN: {d['serial']} ---")
            pm = ThorlabsPM100USB(d["resource_string"])
            print(f"  IDN       : {pm.id}")
            print(f"  Wavelength: {pm.wavelength} nm")
            print(f"  Power     : {pm.power * 1e3:.6f} mW")
            pm.shutdown()