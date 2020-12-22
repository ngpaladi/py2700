=======================
Measurement Types
=======================

The :class:`MeasurementType` class is used to set channel reading types for a 2700 series multimeter. The following examples assume we are setting channels 101,102, and 103 to the specified measurement type.

Voltage
-------------

A channel can be set to read in either DC or AC voltage. Ranging can optionally be provided as an integer but is set to automatic by default. Ranges specified outside the capabilities of the device will be set to automatic.

DC Voltage
*******************

.. code-block::

    my_multimeter.define_channels([101,102,103],
        py2700.MeasurementType.dc_voltage())


AC Voltage
*******************
.. code-block::

    my_multimeter.define_channels([101,102,103],
        py2700.MeasurementType.ac_voltage())


Current
-------------
A channel can be set to read in either DC or AC currents. Ranging can optionally be provided as an integer but is set to automatic by default. Ranges specified outside the capabilities of the device will be set to automatic.

DC Current
*******************
.. code-block::

    my_multimeter.define_channels([101,102,103],
        py2700.MeasurementType.dc_current())


AC Current
*******************
.. code-block::

    my_multimeter.define_channels([101,102,103],
        py2700.MeasurementType.ac_current())


Resistance
------------------
A channel can also be set to read in resistance. Ranging can optionally be provided as an integer but is set to automatic by default. Ranges specified outside the capabilities of the device will be set to automatic.

.. code-block::

    my_multimeter.define_channels([101,102,103],
        py2700.MeasurementType.resistance())


Temperature
-----------------
The Keithley 2700 can read in data from a variety of temperature probe types.

First, ensure you have set units for temperature :
(`C`,`F`, or `K`):

.. code-block::

    my_multimeter.set_temperature_units('C')

Thermocouple
***************
Thermocouples can be of the type J, K, N, T, E, R, S, or B with junction type internal (:code:`INT`), external (:code:`EXT`), or simulated (:code:`SIM`). The default junction type is internal. Using a simulated reference junction requires an additional float to set the simulated junction temperature (0 by default).

.. code-block::

    my_multimeter.define_channels([101,102,103],
        py2700.MeasurementType.thermocouple('K','SIM',5.0))


FRTD
***************
FRTD types of PT100, D100, F100, PT385, PT3916 are supported.

.. code-block::

    my_multimeter.define_channels([101,102,103],
        py2700.MeasurementType.frtd('F100'))


Thermistor
***************
Thermistors are supported, but the resistance type must be passed as an integer. Unsupported values will throw an exception.

.. code-block::

    my_multimeter.define_channels([101,102,103],
        py2700.MeasurementType.thermistor(1000))
