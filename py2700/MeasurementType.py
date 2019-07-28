# Defines Measurement Types

# Define Exceptions
invalid_setup_commands_exception = Exception("This is not a list of strings")
invalid_thermocouple_type_exception = Exception(
    "Not a suppoorted thermocouple type")
invalid_thermistor_type_exception = Exception(
    "Not a suppoorted thermistor type")


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
    def thermocouple(cls, thermocouple_type: str):
        # Defines a Thermocouple

        thermocouple_type = thermocouple_type.upper()
        if not (thermocouple_type in ['J', 'K', 'N', 'T', 'E', 'R', 'S', 'B']):
            raise invalid_thermocouple_type_exception
        setup_commands = ["FUNC 'TEMP'", "TEMP:TRAN TC",
                          "TEMP:TC:TYPE "+str(thermocouple_type), "TEMP:TC:RJUN:RSEL INT"]

        return MeasurementType("TC", "TEMP", setup_commands)

    @classmethod
    def thermistor(cls, resistance_type: int):
        # Defines a Thermistor

        if resistance_type > 10000:
            raise invalid_thermistor_type_exception
        setup_commands = ["FUNC 'TEMP'", "TEMP:TRAN THER",
                          "TEMP:THER:TYPE "+str(resistance_type)]
        return MeasurementType("THER", "TEMP", setup_commands)

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
