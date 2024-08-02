"""
==============
Multimeter.py
==============

"""

from py2700.MeasurementType import MeasurementType
import time
import re
import pyvisa as visa

invalid_unit_exception = Exception("Invalid Unit Type - Please Use 'C', 'K', or 'F'")
not_set_up_exception = Exception("Multimeter not set up properly")
no_channels_exception = Exception("No channels have been defined to set up")


def convert_to_float(string: str) -> float:
    """
    Converts a string containing figures and letters to a float omitting all letters.

    Args:
        string (str): Input string containing figures and letters.

    Returns:
        float: Converted float value.
    """
    # Regular expression pattern to match a number in scientific notation
    pattern = r"[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?"

    # Find the first occurrence of the pattern in the string
    match = re.search(pattern, string)

    # If a match is found, return the float value of the matched string
    if match:
        return float(match.group())
    else:
        raise ValueError("No valid number found in the string")


def list_devices():
    return visa.ResourceManager().list_resources()


class Channel:
    """
    The :class:`Channel` class associates each channel on the multimeter with a :class:`MeasurementType` and performs the necessary initialization procedure.
    """

    def __init__(self, id: int, measurement_type: MeasurementType, unit: str):
        self.id = id
        self.measurement_type = measurement_type
        self.unit = unit

        clist = ",(@" + str(self.id) + ")"
        self.setup_commands = []
        for line in self.measurement_type.setup_commands:
            self.setup_commands.append(line + clist)

    def __str__(self):
        return str(self.id)


class Measurement:
    """
    The :class:`Measurement` class stores a reading taken from a particular channel.
    """

    # Measurement Definition
    def __init__(self, channel: Channel, time: float, value: float):
        self.channel_id = int(channel.id)
        self.time = float(time)
        self.value = float(value)
        self.unit = str(channel.unit)


class ScanResult:
    """
    The :class:`ScanResult` class exists for ease of reading returned values. The attribute :class:`ScanResult.readings` is a dictionary of :class:`Measurement` objects with channel IDs (int) as keys.
    """

    def __init__(
        self,
        channels: list,
        raw_result: list,
        timestamp: float,
        rounding: int,
        user_timestamp: bool,
    ):
        self.raw_result = list(raw_result)
        self.channels = list(channels)
        self.readings = {}
        self.timestamp = timestamp
        self.device_time = 0.0

        entry_index: int = 0
        channel_index: int = 0
        last_value = 0.0

        for entry in raw_result:
            if entry_index % 3 == 0:
                last_value = convert_to_float(entry)

            # If there is no user specific timestamp, then the relative time will be used. The timestamp is not 0 after the first scan.
            # Just in case, if it appears to be be, then it will be forced to 1 µs.
            if entry_index % 3 == 1:
                if not user_timestamp:
                    if self.timestamp != 0:
                        self.timestamp = convert_to_float(entry) - self.timestamp
                    self.device_time = convert_to_float(entry)

                    if self.device_time == 0:
                        self.device_time = 1e-6

                self.readings[channels[channel_index].id] = Measurement(
                    channels[channel_index],
                    round(self.timestamp, rounding),
                    last_value,
                )
                channel_index += 1
            entry_index += 1

    def make_csv_row(self) -> str:
        """Generate a CSV format row of readings in sequence.

        Returns
        -------
        str
            A string representing a row in CSV format of the data values obtained during a measurement.
        """
        string = ""
        for channel in self.channels:
            string = (
                string
                + str(self.readings[channel.id].time)
                + ","
                + str(self.readings[channel.id].value)
                + ","
            )
        return string[:-1] + "\n"

    def make_csv_header(self) -> str:
        """Generate a CSV format row of column headings for readings.

        Returns
        -------
        str
            A string giving headers for a CSV file corresponding to the CSV format for data output.
        """
        string = ""
        for channel in self.channels:
            string = (
                string
                + "Channel "
                + str(channel.id)
                + " Time (s),Channel "
                + str(channel.id)
                + " Value ("
                + str(channel.unit)
                + "),"
            )
        return string[:-1] + "\n"

    def __str__(self) -> str:
        return str(self.raw_result)


class Multimeter:
    """The :class:`Multimeter` class serves as an interface for the digital multimeter. It starts a VISA resource manager with a given

    Parameters
    ----------
    connection_string : str
        The string used to connect to the multimeter, typically something like :code:`TCPIP::192.168.69.102::1394::SOCKET` for a multimeter attached to the network with an IP address of 192.168.69.102 and receiving commands using a socket connection to port 1394.
    timeout : int, optional
        The number of milliseconds to wait before the connection for a given command sent to the multimeter times out, by default 0

    Raises
    ------
    invalid_unit_exception
        Raised when an invalid type of unit is defined for a channel.
    no_channels_exception
        Raised when channels to measure have not been defined.
    not_set_up_exception
        Raised when the channel setup process has not been completed.
    """

    # Class for interacting with the multimeter

    def __init__(self, connection_string: str, timeout: int = 0):
        """Initialize the :class:`Multimeter` object.

        Parameters
        ----------
        connection_string : str
            The string used to connect to the multimeter, typically something like :code:`TCPIP::192.168.69.102::1394::SOCKET` for a multimeter attached to the network with an IP address of 192.168.69.102 and receiving commands using a socket connection to port 1394.
        timeout : int, optional
            The number of milliseconds to wait before the connection for a given command sent to the multimeter times out, by default 0
        """
        self.connection_string = connection_string
        self.channels = []
        self.connected = False
        self.setup = False
        self.temperature_units = "C"
        self.first_scan = True

        # Start visa resource manager
        self.resource_manager = visa.ResourceManager("@py")

        # Open connection to the Keithley 2700 device and configure read/write termination
        self.device = self.resource_manager.open_resource(connection_string)
        self.device.read_termination = "\n"
        self.device.write_termination = "\n"

        # Reset and clear device
        self.device.write("*RST")
        self.device.write("*CLS")
        self.device.write("TRAC:CLE")

        # Setup display
        self.device.write("DISP:TEXT:STAT ON")
        self.display("READY")

        self.connected = True

    def set_temperature_units(self, temperature_units: str) -> None:
        """This sets the units used when reading in the temperature from a temperature probe.

        Parameters
        ----------
        temperature_units : str
            The units for temperature probes (:code:`C`,:code:`F`, or :code:`K`).

        Raises
        ------
        invalid_unit_exception
            Raised when an invalid type of unit is defined for a channel.
        """
        temperature_units = temperature_units.upper()

        if temperature_units not in ["K", "F", "C"]:
            raise invalid_unit_exception

        self.temperature_units = temperature_units
        self.device.write("UNIT:TEMP " + self.temperature_units)

    def define_channels(
        self, channel_ids: list, measurement_type: MeasurementType
    ) -> None:
        """Used to define a group of channels to make a certain type of measurement.

        Parameters
        ----------
        channel_ids : list
            A list of one or more integer channel numbers corresponding to a given :class:`MeasurementType`.
        measurement_type : MeasurementType
            A :class:`MeasurementType` corresponding to the type of measurement you would like to make for these channels. Can be manually defined but usually uses a predefined type from :class:`py2700.MeasurementType`.
        """
        units = ""
        match measurement_type.function:
            case "TEMP":
                units = self.temperature_units
            case "VOLT":
                units = "V"
            case "CURR":
                units = "A"
            case "RES":
                units = "Ohms"

        for ch in channel_ids:
            self.channels.append(Channel(ch, measurement_type, units))

    def setup_scan(self) -> None:
        """Must be called before scanning channels. This completes the setup process for the multimeter after all the channels have been defined.

        Raises
        ------
        no_channels_exception
            Raised when channels to measure have not been defined.
        """
        if len(self.channels) <= 0:
            raise no_channels_exception

        list_of_channels_str = ""
        for ch in self.channels:
            list_of_channels_str = list_of_channels_str + str(ch) + ","
        list_of_channels_str = list_of_channels_str[:-1]
        self.list_of_channels_str = list_of_channels_str

        # Start setup for Keithley 2700
        self.device.write("TRAC:CLE")
        self.device.write("INIT:CONT OFF")
        self.device.write("TRIG:COUN 1")

        for ch in self.channels:
            for line in ch.setup_commands:
                self.device.write(line)

        self.device.write("SAMP:COUN " + str(len(self.channels)))
        self.device.write("ROUT:SCAN (@" + self.list_of_channels_str + ")")

        self.device.write("ROUT:SCAN:TSO IMM")
        self.device.write("ROUT:SCAN:LSEL INT")

        self.setup = True

    def scan(self, timestamp: float = 0, rounding: int = 2) -> ScanResult:
        """[summary]
        If the it is the first scan and no specific timestamp is given, then the device's time will be used for timestamping starting with 0, since the device starts not to count from 0 necessarily.
        In the following scans, the device's old time will be used for reference.

        Parameters
        ----------
        timestamp : float
            If timestamp is other than 0, then the input timestamp will be used.

        rounding : float
            Sets the number of decimals for the rounding of the timestamp value in ScanResult.

        Returns
        -------
        ScanResult
            Returns a :class:`ScanResult` object that contains the result of the last scan.

        Raises
        ------
        not_set_up_exception
            Raised when the channel setup process has not been completed.
        """
        if not self.setup:
            raise not_set_up_exception

        if self.first_scan and timestamp == 0:
            self.first_scan = False
            return self.get_scan_result(timestamp, rounding, False)

        elif not self.first_scan and timestamp == 0:
            former_time = (
                self.last_scan_result.device_time - self.last_scan_result.timestamp
            )
            return self.get_scan_result(former_time, rounding, False)

        else:
            self.first_scan = False
            return self.get_scan_result(timestamp, rounding, True)

    def get_scan_result(
        self, timestamp: float, rounding: int, user_timestamp: bool
    ) -> ScanResult:
        self.last_scan_result = ScanResult(
            self.channels,
            [x.strip() for x in self.device.query("READ?").split(",")],
            timestamp,
            rounding,
            user_timestamp,
        )
        return self.last_scan_result

    def set_timeout(self, timeout: int) -> None:
        self.device.timeout = timeout

    def identify(self) -> str:
        return self.device.query("*IDN?")

    def display(self, string: str) -> None:
        self.device.write("DISP:TEXT:DATA '" + string + "'")

    def disconnect(self) -> None:
        # close the socket connection
        self.display("CLOSING")
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

    def make_csv_header(self) -> str:
        if not self.setup:
            raise not_set_up_exception

        string = ""
        for channel in self.channels:
            string = (
                string
                + "Channel "
                + str(channel.id)
                + " Time (s),Channel "
                + str(channel.id)
                + " Value ("
                + str(channel.unit)
                + "),"
            )
        return string[:-1] + "\n"

    def __str__(self) -> str:
        if self.connected:
            return (
                "Connected to device "
                + str(self.connection_string)
                + "\n"
                + self.identify()
            )
        else:
            return "Device " + str(self.connection_string) + " is not yet connected"
