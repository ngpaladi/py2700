# Defines Measurement Types

# Define Exceptions
invalid_setup_commands_exception = Exception("This is not a list of strings")
invalid_thermocouple_type_exception = Exception(
    "Not a suppoorted thermocouple type")
invalid_thermistor_type_exception = Exception(
    "Not a suppoorted thermistor type")
invalid_reference_junction_type_exception = Exception("Invalid junction type: Please select EXT, INT, or SIM junction type")
invalid_frtd_type_exception = Exception("Invalid Four-Wire RTD type")

class MeasurementType:

    def __init__(self, name: str, function: str, setup_commands: list):
        # Defines a device

        self.name = name
        self.function = function

        for line in setup_commands:
            if(not isinstance(line, str)):
                raise invalid_setup_commands_exception

        self.setup_commands = list(setup_commands)

    @classmethod
    def thermocouple(cls, thermocouple_type: str, reference_junction_type: str = "INT", reference_junction_temp: float = 0.0):
        # Defines a Thermocouple

        thermocouple_type = thermocouple_type.upper()
        if not (thermocouple_type in ['J', 'K', 'N', 'T', 'E', 'R', 'S', 'B']):
            raise invalid_thermocouple_type_exception
        
        if not reference_junction_type in ['INT', 'EXT', 'SIM']:
            raise invalid_reference_junction_type_exception

        

        setup_commands = ["FUNC 'TEMP'", "TEMP:TRAN TC",
                          "TEMP:TC:TYPE "+str(thermocouple_type), "TEMP:TC:RJUN:RSEL "+reference_junction_type]
        if reference_junction_type == "SIM":
            setup_commands.append("TEMP:TC:RJUN:SIM "+str(reference_junction_temp))

        return MeasurementType("TC", "TEMP", setup_commands)

    @classmethod
    def thermistor(cls, resistance_type: int):
        # Defines a Thermistor

        if resistance_type > 10000:
            raise invalid_thermistor_type_exception
        setup_commands = ["FUNC 'TEMP'", "TEMP:TRAN THER",
                          "TEMP:THER "+str(resistance_type)]
        return MeasurementType("THER", "TEMP", setup_commands)
    
    @classmethod
    def frtd(cls, frtd_type: str):
        # Defines a Four-wire RTD

        if not (frtd_type in ['PT100','D100','F100','PT385', 'PT3916']):
            raise invalid_frtd_type_exception
        setup_commands = ["FUNC 'TEMP'", "TEMP:TRAN FRTD",
                          "TEMP:FRTD:TYPE "+str(frtd_type)]
        return MeasurementType("FRTD", "TEMP", setup_commands)

    @classmethod
    def dc_voltage(cls, reading_range: int = -1):
        # Defines a DC voltage reading

        setup_commands = ["FUNC 'VOLT'"]
        if reading_range <= 0 or reading_range > 1010:
            setup_commands.append("VOLT:RANG:AUTO ON")
        else:
            setup_commands.append("VOLT:RANG "+str(reading_range))
        return MeasurementType("DC", "VOLT", setup_commands)

    @classmethod
    def ac_voltage(cls, reading_range: int = -1):
        # Defines an AC voltage reading

        setup_commands = ["FUNC 'VOLT:AC'"]
        if reading_range <= 0 or reading_range > 757:
            setup_commands.append("VOLT:AC:RANG:AUTO ON")
        else:
            setup_commands.append("VOLT:AC:RANG "+str(reading_range))
        return MeasurementType("AC", "VOLT", setup_commands)

    @classmethod
    def dc_current(cls, reading_range: int = -1):
        # Defines a DC current reading

        setup_commands = ["FUNC 'CURR'"]
        if reading_range <= 0 or reading_range > 3:
            setup_commands.append("CURR:RANG:AUTO ON")
        else:
            setup_commands.append("CURR:RANG "+str(reading_range))
        return MeasurementType("DC", "CURR", setup_commands)

    @classmethod
    def ac_current(cls, reading_range: int = -1):
        # Defines a AC current reading

        setup_commands = ["FUNC 'CURR:AC'"]
        if reading_range <= 0 or reading_range > 3:
            setup_commands.append("CURR:AC:RANG:AUTO ON")
        else:
            setup_commands.append("CURR:AC:RANG "+str(reading_range))
        return MeasurementType("AC", "CURR", setup_commands)

    @classmethod
    def resistance(cls, reading_range: int = -1):
        # Defines a resistance reading

        setup_commands = ["FUNC 'RES'"]
        if reading_range <= 0 or reading_range > 120*(10**6):
            setup_commands.append("RES:RANG:AUTO ON")
        else:
            setup_commands.append("RES:RANG "+str(reading_range))
        return MeasurementType("RES", "RES", setup_commands)

    @classmethod
    def fresistance(cls, reading_range: int = -1, averaging: int = -1):
        # Defines a 4-wire resistance reading

        setup_commands = ["FUNC 'FRES'"]
        if reading_range <= 0 or reading_range > 120*(10**6):
            setup_commands.append("FRES:RANG:AUTO ON")
        else:
            setup_commands.append("FRES:RANG "+str(reading_range))

        if averaging > 1:
            setup_commands.append("FRES:NPLC 1")        # repeat-rate: 1 PLC (Medium) (Europe: 50 Hz)
            setup_commands.append("FRES:AVER:WIND 2")   # average within +- 2% value
            setup_commands.append("FRES:AVER:COUN %d" % (averaging))   # average over n samples
            setup_commands.append("FRES:AVER:TCON REP") # repeat-mode (average after reading the n samples)
            setup_commands.append("FRES:AVER:STAT ON")  # turn averaging on

        return MeasurementType("FRES", "FRES", setup_commands)

