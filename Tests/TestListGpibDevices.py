import pyvisa

rm = pyvisa.ResourceManager()
resources = rm.list_resources()

print("Connected devices:")
for r in resources:
    print(r)