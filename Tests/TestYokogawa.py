import pymeasure
from pymeasure.instruments.yokogawa.aq6370series import AQ6375
import numpy as np
import time
import pyvisa

# ─────────────────────────────────────────────
# CONFIGURATION — edit these before running
# ─────────────────────────────────────────────
RESOURCE_ADDRESS = "TCPIP4::192.168.1.100::20001::SOCKET"   # e.g. "TCPIP0::192.168.1.10::inst0::INSTR"
                                        #   or "GPIB0::1::INSTR"
                                        #TCPIP1::192.168.1.100::100001::SOCKET
                                        #TCPIP0::192.168.1.100::INSTR

SWEEP_START_WL   = 1520e-9   # metres  (1520 nm)
SWEEP_STOP_WL    = 1680e-9   # metres  (1580 nm)
RESOLUTION       = 1e-9   # metres  (0.02 nm)
SENSITIVITY      = "MID"     # "HIGH1", "HIGH2", "HIGH3", "MID", "LOW1", "LOW2", "LOW3"
POINTS           = 1001      # number of data points


def connect(address: str) -> AQ6375B:
    """Open a VISA connection to the OSA."""
    print(f"Connecting to OSA at {address} ...")
    #osa = AQ6375B(address)
    #idn = osa.id

    rm = pyvisa.ResourceManager()
    osa = rm.open_resource(address)

    osa.read_termination  = '\n'
    osa.write_termination = '\n'
    osa.timeout           = 1000

    idn = osa.query('*IDN?')
    print(f"Connected  →  {idn.strip()}")
    return osa


def configure(osa: AQ6375B) -> None:
    """Push sweep parameters to the instrument."""
    print("Configuring sweep parameters …")
    osa.wavelength_start    = SWEEP_START_WL
    osa.wavelength_stop     = SWEEP_STOP_WL
    osa.resolution_bandwidth= RESOLUTION
    osa.sensitivity         = SENSITIVITY
    osa.number_of_points    = POINTS
    print(
        f"  Start      : {SWEEP_START_WL*1e9:.3f} nm\n"
        f"  Stop       : {SWEEP_STOP_WL*1e9:.3f} nm\n"
        f"  Resolution : {RESOLUTION*1e9:.4f} nm\n"
        f"  Sensitivity: {SENSITIVITY}\n"
        f"  Points     : {POINTS}"
    )


def run_sweep(osa: AQ6375B) -> None:
    """Trigger a single sweep and block until it completes."""
    print("Starting single sweep …")
    #osa.single_sweep()          # triggers *CLS + :INIT:SMODE SING + :INIT
    osa.write(":INITiate:SMODe SINGle")
    osa.initiate_sweep()
    # Poll *OPC? until the sweep is done (instrument sets bit 0 of ESR)
    timeout_s = 120
    poll_s    = 1.0
    elapsed   = 0.0

    # First wait for sweep to START (bit 0 goes high)
    while elapsed < timeout_s:
        time.sleep(poll_s)
        elapsed += poll_s
        if not (int(osa.ask(":STATus:OPERation:CONDition?")) & 0x01):
            print(f"Sweep started ({elapsed:.0f} s)")
            break
    else:
        raise TimeoutError("Sweep never started")

    # Then wait for sweep to FINISH (bit 0 goes low)
    while elapsed < timeout_s:
        time.sleep(poll_s)
        elapsed += poll_s
        if int(osa.ask(":STATus:OPERation:CONDition?")) & 0x01:        
            print(f"Sweep complete ({elapsed:.0f} s)")
            break
    else:
        raise TimeoutError(f"Sweep did not finish within {timeout_s} s")


def retrieve_data(osa: AQ6375B) -> tuple[np.ndarray, np.ndarray]:
    """Download wavelength & power arrays from trace A."""
    print("Retrieving trace data …")
    wavelengths = np.array(osa.ask(":TRACE:X? TRA").split(","), dtype=float)   # returns numpy array, metres
    powers      = np.array(osa.ask(":TRACE:Y? TRA").split(","), dtype=float)        # returns numpy array, dBm
    print(f"{wavelengths}")
    print(f"  Retrieved {len(wavelengths)} points")
    return wavelengths, powers


def save_data(wavelengths: np.ndarray, powers: np.ndarray,
              filename: str = "osa_scan.csv") -> None:
    """Write results to a simple CSV."""
    header = "wavelength_nm,power_dBm"
    data   = np.column_stack((wavelengths * 1e9, powers))
    np.savetxt(filename, data, delimiter=",", header=header, comments="")
    print(f"Data saved to '{filename}'")


def disconnect(osa: AQ6375B) -> None:
    """Return the OSA to local control and close the VISA session."""
    print("Closing connection …")
    #osa.local()     # :SYST:COMM:LOCK OFF  — returns front-panel control
    osa.shutdown()  # closes the underlying VISA resource
    print("Connection closed.")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main() -> None:
    osa = None
    try:
        osa = connect(RESOURCE_ADDRESS)
        configure(osa)
        run_sweep(osa)
        wavelengths, powers = retrieve_data(osa)

        # ── quick console summary ──────────────────────────────────────
        peak_idx = np.argmax(powers)
        print(
            f"\n── Scan summary ──────────────────────────────\n"
            f"  Peak power : {powers[peak_idx]:.2f} dBm\n"
            f"  Peak λ     : {wavelengths[peak_idx]*1e9:.4f} nm\n"
            f"  Min power  : {powers.min():.2f} dBm\n"
            f"  Max power  : {powers.max():.2f} dBm\n"
            f"──────────────────────────────────────────────\n"
        )

        save_data(wavelengths, powers)

    finally:
        if osa is not None:
            disconnect(osa)


if __name__ == "__main__":
    main()