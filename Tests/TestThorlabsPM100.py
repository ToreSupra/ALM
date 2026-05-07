# To run this script in Windows:
# & c:/Users/RomanoC/VS_Code/ALM/.venv/Scripts/python.exe C:\Users\RomanoC\VS_Code\ALM\TestThorlabsPM100.py

from pymeasure.instruments.thorlabs import ThorlabsPM100USB

# Connect to the instrument (adjust the resource string to match your connection)
# USB example:
pm = ThorlabsPM100USB("USB0::4883::32888::P0048724::0::INSTR")

# --- Identification ---
print("Part Number (PN):", pm.id)          # Returns full IDN string (includes PN)
print("Sensor Info:", pm.name)      # Returns PN, SN, cal date, sensor type, etc.

# --- Serial Number ---
# The sensor_info property returns a named tuple with detailed info
print("Sensor PN:", pm.sensor_name)
print("Sensor SN:", pm.sensor_sn)

# --- Set Wavelength ---
pm.wavelength = 1731   # Set wavelength in nm (e.g., 1731)
print("Wavelength set to:", pm.wavelength, "nm")

# --- Read Power ---
power = pm.power          # Returns power in Watts
print(f"Power: {power * 1e6:.4f} µW")    # Convert to µW for small signals
print(f"Power: {power * 1e3:.6f} mW")

# --- Cleanup ---
pm.shutdown()