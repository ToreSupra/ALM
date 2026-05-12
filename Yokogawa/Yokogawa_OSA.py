from pymeasure.instruments import Instrument
from pymeasure.instruments.yokogawa.aq6370series import AQ6375
from pymeasure.adapters import VISAAdapter
import warnings
import time
import re

class AQ6375Lan(AQ6375):

    def __init__(self, host: str, port: int = 10001, username: str = "anonymous", password: str = "", verbose: bool = False):
        self.verbose = verbose
        resource_string = f"TCPIP0::{host}::{port}::SOCKET"

        adapter = VISAAdapter(
            resource_string,
            read_termination="\r\n",
            write_termination="\r\n",
            timeout=10000,
            chunk_size=1024 * 1024,
        )

        self._authenticate(adapter, username, password, self.verbose)

        warnings.filterwarnings("ignore", category=FutureWarning, module="pymeasure")
        # Call the top-level Instrument.__init__ directly, skipping AQ6370Series
        Instrument.__init__(self, adapter, "Yokogawa AQ6375", includeSCPI=True)

    @staticmethod
    def _authenticate(adapter, username: str, password: str, verbose: bool) -> None:
        adapter.write(f'OPEN "{username}"')
        challenge = adapter.read()
        if verbose:
            print(f"Auth challenge: {challenge.strip()}")

        if "authenticate" not in challenge.strip().lower():
            raise ConnectionError(f"Unexpected auth response: {challenge!r}")

        adapter.write(password)
        result = adapter.read()
        if verbose:
            print(f"Auth result: {result.strip()}")

        if "ready" not in result.strip().lower():
            raise ConnectionError(f"Authentication failed: {result!r}")

        if verbose:
            print("Authentication successful.")

    def close(self) -> None:
        try:
            self.write("CLOSE")
        except Exception:
            pass
        self.shutdown()

    def run_sweep(self, timeout_s: int = 120, poll_s: float = 1.0) -> None:
        """
        Trigger a single sweep and block until it completes.

        :param timeout_s: Maximum time to wait for sweep completion in seconds.
        :param poll_s:    Polling interval in seconds.
        """
        if self.verbose:
            print("Starting single sweep …")
        self.write(":INITiate:SMODe SINGle")
        self.write(":INITiate")

        elapsed = 0.0

        # Wait for sweep to START (bit 0 goes low)
        #while elapsed < timeout_s:
        #    time.sleep(poll_s)
        #    elapsed += poll_s
        #    if not (int(self.ask(":STATus:OPERation:CONDition?")) & 0x01):
        #        print(f"  Sweep started ({elapsed:.0f} s)")
        #        break
        #else:
        #    raise TimeoutError("Sweep never started")

        time.sleep(1)

        # Wait for sweep to FINISH (bit 0 goes high)
        while elapsed < timeout_s:
            time.sleep(poll_s)
            elapsed += poll_s
            if int(self.ask(":STATus:OPERation:CONDition?")) & 0x01:
                if self.verbose:
                    print(f"  Sweep complete ({elapsed:.0f} s)")
                break
        else:
            raise TimeoutError(f"Sweep did not finish within {timeout_s} s")

    def calculate_power(self, trace: str = "TRA") -> str:
        """
        Run the Power analysis on the given trace and return the raw
        result string from the instrument.

        Procedure (from manual section 7.6):
          1. :CALCulate:CATegory POWer   — select analysis type
          2. :CALCulate[:IMMediate]       — execute analysis
          3. :CALCulate:DATA?             — retrieve results

        :param trace: Trace to analyse: TRA–TRG (default "TRA").
        :returns:     Raw comma-separated result string from the instrument.

        Manual ref: CALCulate:CATegory POWer (category 9)
        """
        # Step 1 — select the active trace
        self.write(f":TRACe:ACTive {trace}")

        # Step 2 — select Power analysis category
        self.write(":CALCulate:CATegory POWer")

        # Step 3 — execute analysis
        self.write(":CALCulate")

        # Step 4 — retrieve result
        result = self.ask(":CALCulate:DATA?")
        return result
    
    def save_trace_to_usb(self, filename: str, trace: str = "TRA",
                          fmt: str = "CSV") -> None:
        """
        Save a trace to the USB flash drive connected to the OSA.

        :param filename: Filename without extension (max 56 chars).
                         e.g. "my_scan" → saved as "my_scan.csv" on the USB.
        :param trace:    Trace to save: TRA–TRG (default "TRA").
        :param fmt:      File format: "CSV" or "BIN" (default "CSV").

        Manual ref: :MMEMory:STORe:TRACe <trace>,BIN|CSV,"<filename>",EXTernal
        """
        fmt = fmt.upper()
        if fmt not in ("CSV", "BIN"):
            raise ValueError(f"fmt must be 'CSV' or 'BIN', got {fmt!r}")
        trace = trace.upper()

        cmd = f':MMEMory:STORe:TRACe {trace},{fmt},"{filename}",EXTernal'
        self.write(cmd)
        if self.verbose:
            print(f"Trace {trace} saved to USB as '{filename}.{fmt.lower()}'")

    def list_usb_files(self, directory: str = "") -> list[dict]:
        """
        Return a list of files on the USB flash drive.

        :param directory: Optional subdirectory path on the USB,
                        e.g. "\\measurements\\2026". 
                        If empty, lists the root of the USB drive.
        :returns: List of dicts with keys:
                - 'name'      : str  — filename including extension
                - 'free_kb'   : float — free space remaining on USB [KB]

        Response format from instrument (manual ref: :MMEMory:CATalog?):
        <free_size>,<file_count>,<file_name>,<file_name>,...

        Example::
            files = osa.list_usb_files()
            for f in files:
                print(f['name'])

            # List a subdirectory
            files = osa.list_usb_files(directory="\\\\scans\\\\2026")
        """
        if directory:
            cmd = f':MMEMory:CATalog? EXTernal,"{directory}"'
        else:
            cmd = ":MMEMory:CATalog? EXTernal"

        response = self.ask(cmd)
        parts = response.split(",")

        # First field: free disk space in KB
        # Second field: number of files
        # Remaining fields: filenames
        free_kb    = float(parts[0])
        file_count = int(parts[1])
        filenames  = parts[2:2 + file_count]

        if self.verbose:
            print(f"USB free space: {free_kb / 1024:.1f} MB — {file_count} file(s) found")

        return [{"name": name.strip(), "free_kb": free_kb} for name in filenames]
    
    def next_usb_filename(self) -> str:
        """
        Scan the USB drive for files matching the pattern W####.CSV,
        find the highest number, and return the next filename.

        Returns "W0000.CSV" if no matching files exist yet.

        Example::
            filename = osa.next_usb_filename()
            # -> "W0042.CSV"
            osa.save_trace_to_usb(filename=filename.replace(".CSV", ""))
        """
        files = self.list_usb_files()

        pattern = re.compile(r'^W(\d{4})\.CSV$', re.IGNORECASE)

        numbers = []
        for f in files:
            match = pattern.match(f['name'])
            if match:
                numbers.append(int(match.group(1)))

        next_number = (max(numbers) + 1) if numbers else 0

        if next_number > 9999:
            raise OverflowError("USB file counter exceeded W9999.CSV — please archive and clear files.")

        filename = f"W{next_number:04d}.CSV"
        if self.verbose:
            print(f"Next filename: {filename}")
        return filename
    
    def set_analysis_range(self, mode: str) -> None:
        """
        Switch the analysis/calculation range between the full sweep
        or the region bounded by line markers L1 and L2.

        :param mode: "full"    — analyse the entire sweep range (SRANGE OFF)
                    "markers" — analyse only between line markers L1 and L2
                                (SRANGE ON)

        Note: This uses LINE markers L1 and L2 (set via set_line_marker()),
        NOT the fixed markers 1–4 (set via set_marker()).
        Line markers are the vertical wavelength cursors on the display.

        Manual ref: :CALCulate:LMARker:SRANge OFF|ON
        """
        mode = mode.strip().lower()
        if mode not in ("full", "markers"):
            raise ValueError(f"mode must be 'full' or 'markers', got {mode!r}")

        scpi_value = "ON" if mode == "markers" else "OFF"
        self.write(f":CALCulate:LMARker:SRANge {scpi_value}")
        if self.verbose:
            print(f"Analysis range set to: {'L1–L2 marker region' if mode == 'markers' else 'full sweep'}")


    def set_line_marker(self, marker: int, wavelength_m: float) -> None:
        """
        Set the position of line marker L1 or L2 (the vertical wavelength
        cursors that define the analysis range).

        :param marker:       Line marker number: 1 (L1) or 2 (L2).
        :param wavelength_m: Wavelength position in metres (e.g. 1540e-9).

        Manual ref: :CALCulate:LMARker:X <1|2>, <NRf>[M]
        """
        if marker not in (1, 2):
            raise ValueError(f"Line marker must be 1 or 2, got {marker!r}")

        self.write(f":CALCulate:LMARker:X {marker},{wavelength_m:.6E}M")
        if self.verbose:
            print(f"Line marker L{marker} set at {wavelength_m * 1e9:.4f} nm")


    def get_analysis_range(self) -> str:
        """
        Query the current analysis range mode.

        :returns: "markers" if limited to L1–L2, "full" otherwise.

        Manual ref: :CALCulate:LMARker:SRANge?
        """
        response = self.ask(":CALCulate:LMARker:SRANge?")
        mode = "markers" if response.strip() == "1" else "full"
        if self.verbose:
            print(f"Analysis range: {mode}")
        return mode
    
    # Valid sensitivity modes for the AQ6375
    # HIGH1/2/3 engage the chopper automatically on this model
    AQ6375_SENSITIVITY_MODES = {
        "NHLD":   "Norm/Hold  — no sweep triggered",
        "NAUT":   "Norm/Auto  — auto sweep",
        "NORMAL": "Normal",
        "MID":    "Mid",
        "HIGH1":  "High1/Chop (chopper on)",
        "HIGH2":  "High2/Chop (chopper on)",
        "HIGH3":  "High3/Chop (chopper on)",
    }

    def set_sensitivity(self, mode: str) -> None:
        """
        Set the measurement sensitivity mode of the AQ6375.

        On the AQ6375, HIGH1/HIGH2/HIGH3 automatically engage the
        optical chopper (displayed as HIGH1/CHOP etc. on the front panel).

        :param mode: One of:
                    "NHLD"   — Norm/Hold
                    "NAUT"   — Norm/Auto
                    "NORMAL" — Normal
                    "MID"    — Mid        (default, good balance)
                    "HIGH1"  — High1/Chop (slower, lower noise floor)
                    "HIGH2"  — High2/Chop
                    "HIGH3"  — High3/Chop (slowest, best sensitivity)

        Manual ref: :SENSe:SENSe NHLD|NAUT|NORMal|MID|HIGH1|HIGH2|HIGH3
        """
        mode = mode.strip().upper()

        # Accept "NORM" as alias for "NORMAL"
        if mode == "NORM":
            mode = "NORMAL"

        if mode not in self.AQ6375_SENSITIVITY_MODES:
            raise ValueError(
                f"Invalid sensitivity mode {mode!r}. "
                f"Choose from: {list(self.AQ6375_SENSITIVITY_MODES)}"
            )

        # Map NORMAL → NORMal for the SCPI command
        scpi_value = "NORMal" if mode == "NORMAL" else mode
        self.write(f":SENSe:SENSe {scpi_value}")
        if self.verbose:
            print(f"Sensitivity set to: {mode}  ({self.AQ6375_SENSITIVITY_MODES[mode]})")


    def get_sensitivity(self) -> str:
        """
        Query the current sensitivity mode.

        :returns: Current mode string, e.g. "MID", "HIGH1", "NORMAL" …

        Manual ref: :SENSe:SENSe?
        """
        response = self.ask(":SENSe:SENSe?")
        # Instrument returns numeric code: 0=NHLD,1=NAUT,2=MID,3=HIGH1,4=HIGH2,5=HIGH3,6=NORMAL
        code_map = {
            "0": "NHLD",
            "1": "NAUT",
            "2": "MID",
            "3": "HIGH1",
            "4": "HIGH2",
            "5": "HIGH3",
            "6": "NORMAL",
        }
        mode = code_map.get(response.strip(), response.strip())
        if self.verbose:
            print(f"Current sensitivity: {mode}")
        return mode
    # Valid trace attribute modes for the AQ6375
    AQ6375_TRACE_MODES = {
        "WRITE": ("WRITe", "Active trace — updated on every sweep"),
        "FIX":   ("FIX",   "Fixed — trace is frozen, not updated"),
        "MAX":   ("MAX",   "Max hold — retains the maximum at each point"),
        "MIN":   ("MIN",   "Min hold — retains the minimum at each point"),
    }

    VALID_TRACES = ("TRA", "TRB", "TRC", "TRD", "TRE", "TRF", "TRG")


    def set_trace_mode(self, trace: str, mode: str) -> None:
        """
        Set the acquisition mode of a trace.

        :param trace: Trace name: TRA–TRG.
        :param mode:  One of:
                        "WRITE" — updated on every sweep (default active trace)
                        "FIX"   — frozen, not updated by sweeps
                        "MAX"   — max hold across sweeps
                        "MIN"   — min hold across sweeps

        Manual ref: :TRACe:ATTRibute:<trace> WRITe|FIX|MAX|MIN
        """
        trace = trace.strip().upper()
        mode  = mode.strip().upper()

        if trace not in self.VALID_TRACES:
            raise ValueError(f"Invalid trace {trace!r}. Choose from: {self.VALID_TRACES}")
        if mode not in self.AQ6375_TRACE_MODES:
            raise ValueError(
                f"Invalid mode {mode!r}. "
                f"Choose from: {list(self.AQ6375_TRACE_MODES)}"
            )

        scpi_value, description = self.AQ6375_TRACE_MODES[mode]
        self.write(f":TRACe:ATTRibute:{trace} {scpi_value}")
        if self.verbose:
            print(f"Trace {trace} set to {mode} — {description}")


    def get_trace_mode(self, trace: str) -> str:
        """
        Query the current acquisition mode of a trace.

        :param trace: Trace name: TRA–TRG.
        :returns:     Current mode string: "WRITE", "FIX", "MAX" or "MIN".

        Manual ref: :TRACe:ATTRibute:<trace>?
        """
        trace = trace.strip().upper()
        if trace not in self.VALID_TRACES:
            raise ValueError(f"Invalid trace {trace!r}. Choose from: {self.VALID_TRACES}")

        response = self.ask(f":TRACe:ATTRibute:{trace}?")
        # Instrument returns numeric code: 0=WRITE, 1=FIX, 2=MAX, 3=MIN
        code_map = {"0": "WRITE", "1": "FIX", "2": "MAX", "3": "MIN"}
        mode = code_map.get(response.strip(), response.strip())
        if self.verbose:
            print(f"Trace {trace} mode: {mode}")
        return mode
    
    def set_auto_zero(self, enabled: bool) -> None:
        """
        Enable or disable the automatic offset (zero) calibration.

        When disabled, the OSA will no longer interrupt sweeps to perform
        periodic noise floor calibration. Disable this when you need
        uninterrupted back-to-back sweeps.

        Note: The interval control (:CALibration:ZERO:INTerval) is only
        available on the AQ6373, not the AQ6375.

        :param enabled: True to enable auto-zero, False to disable it.

        Manual ref: :CALibration:ZERO[:AUTO] OFF|ON
        """
        value = "ON" if enabled else "OFF"
        self.write(f":CALibration:ZERO {value}")
        if self.verbose:
            print(f"Auto zero calibration: {'enabled' if enabled else 'disabled'}")


    def get_auto_zero(self) -> bool:
        """
        Query whether auto zero calibration is currently enabled.

        :returns: True if enabled, False if disabled.

        Manual ref: :CALibration:ZERO[:AUTO]?
        """
        response = self.ask(":CALibration:ZERO?")
        enabled = response.strip() == "1"
        if self.verbose:
            print(f"Auto zero calibration: {'enabled' if enabled else 'disabled'}")
        return enabled


    def zero_once(self) -> None:
        """
        Trigger a single offset calibration immediately, without
        changing the auto-zero ON/OFF setting.

        The instrument must be in sweep-stopped state before calling this.
        Use get_zero_status() to poll completion.

        Manual ref: :CALibration:ZERO ONCE
        """
        self.write(":CALibration:ZERO ONCE")
        if self.verbose:
            print("Zero calibration triggered (once)")


    def get_zero_status(self) -> bool:
        """
        Query whether an offset calibration is currently in progress.

        :returns: True if zeroing is running, False if complete/idle.

        Manual ref: :CALibration:ZERO[:AUTO]:STATus?
        """
        response = self.ask(":CALibration:ZERO:STATus?")
        running = response.strip() == "1"
        if self.verbose:
            print(f"Zero calibration {'in progress' if running else 'idle'}")
        return running
    
    def calculate_wdm_snr(self, trace: str = "TRA") -> list[float]:
        """
        Run WDM analysis on the given trace and return the SNR value(s)
        in dB, one per detected channel.

        Note: OSNR category is not available on the AQ6375. WDM (category 11)
        is used instead, which provides the same SNR result via CSNR?.

        :param trace: Trace to analyse: TRA–TRG (default "TRA").
        :returns:     List of SNR values in dB, one per channel.
                    Single-channel example: [40.0]
                    Multi-channel example:  [38.5, 39.1, 40.2]

        Manual ref:
        :CALCulate:CATegory WDM          — select WDM analysis
        :CALCulate[:IMMediate]            — execute
        :CALCulate:DATA:NCHannels?        — get number of channels found
        :CALCulate:DATA:CSNR?             — get SNR per channel [dB]
        """
        trace = trace.strip().upper()
        if trace not in self.VALID_TRACES:
            raise ValueError(f"Invalid trace {trace!r}. Choose from: {self.VALID_TRACES}")

        # Step 1 — select active trace
        self.write(f":TRACe:ACTive {trace}")

        # Step 2 — select WDM analysis (OSNR not available on AQ6375)
        self.write(":CALCulate:CATegory WDM")

        # Step 3 — execute analysis
        self.write(":CALCulate")

        # Step 4 — check how many channels were detected
        n_channels = int(self.ask(":CALCulate:DATA:NCHannels?"))
        if self.verbose:
            print(f"  WDM channels detected: {n_channels}")

        if n_channels == 0:
            if self.verbose:
                print("  Warning: no channels detected — check threshold and trace")
            return []

        # Step 5 — retrieve SNR for each channel
        raw = self.ask(":CALCulate:DATA:CSNR?")
        snr_values = [float(v) for v in raw.split(",")]

        if self.verbose:
            for i, snr in enumerate(snr_values):
                print(f"  Channel {i+1}: SNR = {snr:.2f} dB")

        return snr_values
    
    def is_usb_connected(self) -> bool:
        """
        Check whether a USB flash drive is connected to the OSA.

        :param verbose: If True, print status messages (default False).
        :returns:       True if a USB drive is present and accessible.
        """
        try:
            response = self.ask(":MMEMory:CATalog? EXTernal")
            parts = response.strip().split(",")
            if len(parts) >= 2:
                float(parts[0])
                if self.verbose:
                    print("USB drive detected.")
                return True
            else:
                if self.verbose:
                    print("USB drive not detected (unexpected response).")
                return False

        except Exception:
            if self.verbose:
                print("USB drive not detected (query error).")
            return False
    
    def is_signal_present(self,
                      marker1_nm: float,
                      marker2_nm: float,
                      threshold_dBm: float = -40.0,
                      trace: str = "TRA") -> bool:
        """
        Detect whether an optical signal is present between two wavelengths
        using a peak search on the moving marker (marker 0).

        Method:
        1. Set line markers L1/L2 to define the search region
        2. Enable SEARCH/ANA L1-L2 to restrict peak search to that region
        3. Run :CALCulate:MARKer:MAXimum — places moving marker on peak
        4. Read back the peak level via :CALCulate:MARKer:Y? 0
        5. Compare against threshold

        :param marker1_nm:    Left boundary in nm.
        :param marker2_nm:    Right boundary in nm.
        :param threshold_dBm: Power threshold in dBm (default -40.0).
                            Anything above this is considered a signal.
        :param trace:         Trace to search (default "TRA").
        :returns:             True if a peak above threshold is found.

        Manual ref:
        :CALCulate:LMARker:SRANge ON      — restrict search to L1-L2
        :CALCulate:MARKer:MAXimum         — peak search → moving marker
        :CALCulate:MARKer:Y? 0            — read moving marker level
        """
        # Step 1 — set the search region via line markers
        self.set_line_marker(1, marker1_nm * 1e-9)
        self.set_line_marker(2, marker2_nm * 1e-9)

        # Step 2 — restrict peak search to L1-L2 region
        self.set_analysis_range("markers")

        trace = trace.strip().upper()
        if trace not in self.VALID_TRACES:
            raise ValueError(f"Invalid trace {trace!r}. Choose from: {self.VALID_TRACES}")

        # Step 1 — select active trace
        self.write(f":TRACe:ACTive {trace}")

        # Step 2 — select WDM analysis (OSNR not available on AQ6375)
        self.write(":CALCulate:CATegory WDM")

        # Step 3 — execute analysis
        self.write(":CALCulate")

        # Step 4 — check how many channels were detected
        n_channels = int(self.ask(":CALCulate:DATA:NCHannels?"))
        if self.verbose:
            print(f"  WDM channels detected: {n_channels}")

        if n_channels == 0:
            if self.verbose:
                print("  Warning: no channels detected — check threshold and trace")
            return False

        # Step 5 — retrieve SNR for each channel
        raw_power = self.ask(":CALCulate:DATA:CPOWers?")
        power_values = [float(v) for v in raw_power.split(",")] # dBm

        raw_wl = self.ask(":CALCulate:Data:CWAVelengths?")
        wl_values = [float(v) for v in raw_wl.split(",")] # nm

        if self.verbose:
            for i, power in enumerate(power_values):
                print(f"  Channel {i+1}: Peak = {power:.2f} dB")
        
        peak_dBm = max(power_values)
        peak_nm = power_values.index(peak_dBm)

        # Step 6 — compare against threshold
        detected = peak_dBm > threshold_dBm

        if self.verbose:
            print(f"  Signal detection [{marker1_nm:.1f}–{marker2_nm:.1f} nm]: "
                f"peak = {peak_dBm:.2f} dBm @ {peak_nm:.3f} nm — "
                f"{'DETECTED' if detected else 'NOT DETECTED'} "
                f"(threshold = {threshold_dBm:.1f} dBm)")

        # Step 7 — restore full analysis range
        self.set_analysis_range("full")

        return detected


if __name__ == "__main__":
    osa = AQ6375Lan(host="192.168.1.100", port=20001, username="anonymous")

    # All the normal driver properties now work
    print(osa.id)
    osa.wavelength_start     = 1520e-9
    osa.wavelength_stop      = 1680e-9
    osa.resolution_bandwidth = 1e-9
    osa.sensitivity          = "HIGH1"
    osa.set_sensitivity("MID")
    osa.run_sweep()

    print(osa.calculate_power())

    print(osa.next_usb_filename())

    osa.set_line_marker(1, 1540e-9)   # L1 at 1540 nm
    osa.set_line_marker(2, 1560e-9)   # L2 at 1560 nm

    osa.set_analysis_range("markers")

    result = osa.calculate_power(trace="TRA")
    print(result)

    osa.set_analysis_range("full")

    result = osa.calculate_power(trace="TRA")
    print(result)

    osa.close()