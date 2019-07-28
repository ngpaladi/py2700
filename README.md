# Unofficial Keithley 2700 Series DMM Interface: py2700
A Python package to interface with a Keithley 2700 digital multimeter.

## Introduction
The py2700 package is designed to allow for easy access to common SCPI commands sent to the multimeter. From setting up channels, to reading data, to even writing to the display, the package allows the user to quickly and easily produce working, readable Python code to collect data from their device, and ultimately avoid being forced to pay for a license for Keithley Kickstart.

## Example Program
```python 
import py2700 as DMM
import time

# Connect to a Keithley 2701 over TCP/IP
my_multimeter = DMM.Multimeter('TCPIP::192.168.69.102::1394::SOCKET')

# Set the default temperature units
my_multimeter.set_temperature_units('C')

# Set Channels 101, 102, and 103 as K-type thermocouples
my_multimeter.define_channels([101,102,103],
    DMM.MeasurementType.thermocouple('K'))

# Setup for reading: 
#   This needs to be completed after channel
#   definitions and before scanning
my_multimeter.setup_scan()

# Scan the channels, given the timestamp you want 
# for the reading
result = my_multimeter.scan(time.time_ns()/(10**9))

# Print out a CSV header for the result
print(my_multimeter.make_csv_header())

# Print out a CSV row for the result
print(result.make_csv_row())

# Safely disconnect from the multimeter
my_multimeter.disconnect()
```
## Contact
Please submit an issue if you encounter a bug and please email any questions or requests to py2700@noahpaladino.com