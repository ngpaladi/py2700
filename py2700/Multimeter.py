from py2700.MeasurementType import MeasurementType
import time
import pyvisa as visa

invalid_unit_exception = Exception("Invalid Unit Type - Please Use 'C', 'K', or 'F'")
not_set_up_exception = Exception("Multimeter not set up properly")
no_channels_exception = Exception("No channels have been defined to set up")

def RemoveUnits(string: str):
    while not (string[-1] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
        string = string[:-1]
    return string


class Channel:
    # Channel Definition
    def __init__(self, id: int, measurement_type: MeasurementType, unit: str):
        self.id = id
        self.measurement_type = measurement_type
        self.unit = unit

        clist = ",(@"+str(self.id)+")"
        self.setup_commands = []
        for line in self.measurement_type.setup_commands:
            self.setup_commands.append(line+clist)
    
    def __str__(self):
        return str(self.id)


class Measurement:
    # Measurement Definition
    def __init__(self, channel: Channel, time: float, value: float):
        self.channel_id = int(channel.id)
        self.time = float(time)
        self.value = float(value)
        self.unit = str(channel.unit)


class ScanResult:
    # Helper class for ease of reading returned values

    def __init__(self, channels: list, raw_result: list, timestamp: float):
        self.raw_result = list(raw_result)
        self.channels = list(channels)
        self.initial_timestamp = float(timestamp)
        self.readings = {}

        entry_index = 0
        channel_index = 0
        last_value = 0.
        last_time = 0.
        for entry in raw_result:
            if entry_index % 3 == 0:
                last_value = float(RemoveUnits(entry))
            if entry_index % 3 == 1:
                last_time = float(RemoveUnits(entry))
                self.readings[channels[channel_index].id] = Measurement(
                    channels[channel_index], self.initial_timestamp+last_time, last_value)
                channel_index += 1
            entry_index += 1

    def make_csv_row(self):
        string = ""
        for channel in self.channels:
            string = string + \
                str(self.readings[channel.id].time)+"," + \
                str(self.readings[channel.id].value)+","
        return string[:-1]+"\n"

    def make_csv_header(self):
        string = ""
        for channel in self.channels:
            string = string + "Channel " + \
                str(channel.id)+" Time (s),Channel " + \
                str(channel.id)+" Value ("+str(channel.unit)+"),"
        return string[:-1]+"\n"

    def __str__(self):
        return str(self.raw_result)


class Multimeter:
    # Class for interacting with the multimeter

    def __init__(self, connection_string: str, timeout:int = 0):
        self.connection_string = connection_string
        self.channels = []
        self.connected = False
        self.setup = False
        self.temperature_units = 'C'

         # Start visa resource manager
        self.resource_manager = visa.ResourceManager("@py")

        # Open connection to the Keithley 2700 device and configure read/write termination
        self.device = self.resource_manager.open_resource(connection_string)
        self.device.read_termination = '\n'
        self.device.write_termination = '\n'

        # Reset and clear device
        self.device.write("*RST")
        self.device.write("*CLS")
        self.device.write("TRAC:CLE")

        # Setup display
        self.device.write("DISP:TEXT:STAT ON")
        self.device.write("DISP:TEXT:DATA 'READY'")

        self.connected = True
    def set_temperature_units(self, temperature_units:str):
        temperature_units = temperature_units.upper()
        
        if not (temperature_units in ['K','F','C']):
            raise invalid_unit_exception

        self.temperature_units = temperature_units
        self.device.write("UNIT:TEMP "+self.temperature_units)

    def define_channels(self, channel_ids: list, measurement_type: MeasurementType):
        units = ""
        if measurement_type.function == "TEMP":
            units = self.temperature_units
        elif measurement_type.function == "VOLT":
            units = "V"
        elif measurement_type.function == "CURR":
            units = "A"
        elif measurement_type.function == "RES":
            units = "Ohms"

        for ch in channel_ids:
            self.channels.append(Channel(ch,measurement_type, units))

    def setup_scan(self):
        if len(self.channels) <= 0:
            raise no_channels_exception

        list_of_channels_str=""
        for ch in self.channels:
            list_of_channels_str = list_of_channels_str+str(ch)+","
        list_of_channels_str = list_of_channels_str[:-1]
        self.list_of_channels_str = list_of_channels_str

        # Start setup for Keithley 2700
        self.device.write("TRAC:CLE")
        self.device.write("INIT:CONT OFF")
        self.device.write("TRIG:COUN 1")

        for ch in self.channels:
            for line in ch.setup_commands:
                self.device.write(line)

        self.device.write("SAMP:COUN "+str(len(self.channels)))
        self.device.write("ROUT:SCAN (@"+self.list_of_channels_str+")")

        self.device.write("ROUT:SCAN:TSO IMM")
        self.device.write("ROUT:SCAN:LSEL INT")

        self.setup = True
    
    def scan(self, timestamp:float):
        if not self.setup:
            raise not_set_up_exception

        self.last_scan_result = ScanResult(self.channels,
                                           [x.strip() for x in self.device.query("READ?").split(',')], timestamp)
        return self.last_scan_result

    def set_timeout(self, timeout:int ):
        self.device.timeout = timeout

    def identify(self):
        return self.device.query("*IDN?")
    
    def display(self, string: str):
        self.device.write("DISP:TEXT:DATA '"+string+"'")

    def disconnect(self):
        # close the socket connection
        self.device.write("DISP:TEXT:DATA 'CLOSING'")
        time.sleep(3)
        self.device.write("DISP:TEXT:STAT OFF")
        self.device.write("ROUT:OPEN:ALL")

    # The following functions act as "pass-throughs" for SCPI commands
    def write(self, string: str) -> str:
        return self.device.write(string)

    def query(self, string: str) -> str:
        return self.device.query(string)

    def read(self, string: str) -> str:
        return self.device.read(string)

    def make_csv_header(self):
        if not self.setup:
            raise not_set_up_exception
            
        string = ""
        for channel in self.channels:
            string = string + "Channel " + \
                str(channel.id)+" Time (s),Channel " + \
                str(channel.id)+" Value ("+str(channel.unit)+"),"
        return string[:-1]+"\n"

    def __str__(self):
        if self.connected:
            return "Connected to device "+str(self.connection_string)+"\n"+self.identify()
        else:
            return "Device "+str(self.connection_string)+" is not yet connected"
