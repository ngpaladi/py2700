============
Multimeter
============

The multimeter class is used to interact with a 2700 series multimeter.

Connection
---------------
To connect to the device, create a :class:`Multimeter` object, passing the connection string as the initialization parameter. 

In the following example we use a TCP/IP Socket connection to a multimeter at IP address 192.168.69.102 and connecting to port 1394:

.. code-block::

    my_multimeter = py2700.Multimeter('TCPIP::192.168.69.102::1394::SOCKET')


Setting the Timeout
----------------------
It is good practice to set the value for the timeout period of the multimeter next, in milliseconds:

.. code-block::

    my_multimeter.set_timeout(5000)

Setting the Temperature Units
--------------------------------
If you are using temperature probes, set the units (:code:`C`,:code:`F`, or :code:`K`):

.. code-block::

    my_multimeter.set_temperature_units('C')


Setting Up the Channels
--------------------------
Before you can take measurements, you must specify what channels you want to measure and what type of measurement you are taking for each. To set a list of channels to be scanned as the proper measurement types, please use the multimeter object's :class:`define_channels(list of channels, MeasurementType)` function.

In the following example, we set the channels 101, 102, and 103 to act as K type thermocouples, with the default internal reference junction (`INT`):

.. code-block::

    my_multimeter.define_channels([101,102,103],
        py2700.MeasurementType.thermocouple('K'))

After all channels are defined, and before calling the `scan()` function, please run the scan setup function as follows:

.. code-block::

    my_multimeter.setup_scan()

This will set up the multimeter's scan function such that it scans the channels in the order they were set up.

Completing a Scan
----------------------
To scan the channels, call the scan function, passing the timestamp (in seconds) you wish to be associated with the start of the scan, as follows:

.. code-block::

    result = my_multimeter.scan(time.time_ns()/(10**9))


The returned object is of the type [ScanResult](scanresult.md).

Writing a Message on the Screen
---------------------------------
To write a message on the multimeter's screen use the following:

.. code-block::

    my_multimeter.display("HELLO")


Safely Disconnecting
----------------------
To safely disconnect from the multimeter, use the following:

.. code-block::

    my_multimeter.disconnect()


Advanced Usage: SCPI Commands
--------------------------------
To directly read, write, or query the device using the SCPI commands, use the following functions:

.. code-block::

    my_multimeter.write(str)
    my_multimeter.read(str)
    my_multimeter.query(str)
