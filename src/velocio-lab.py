#!/usr/bin/env python
#---------------------------------------------------------------------------#
# Import the various server implementations
#---------------------------------------------------------------------------#
#from pymodbus.client.sync import ModbusTcpClient as ModbusClient
#from pymodbus.client.sync import ModbusUdpClient as ModbusClient
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

#---------------------------------------------------------------------------#
# Configure the client logging
#---------------------------------------------------------------------------#
import logging
logging.basicConfig()
log = logging.getLogger()
#log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------#
# Choose the client you want
#---------------------------------------------------------------------------#
# Here is an example of using these options::
#    plc = ModbusClient('localhost', retries=3, retry_on_empty=True)
#    plc = ModbusClient(method='ascii', port='/dev/pts/2', timeout=1)
#    plc = ModbusClient(method='rtu', port='/dev/ttyACM0', timeout=1)
#    plc.connect()
#---------------------------------------------------------------------------#

with ModbusClient(method='rtu', port='/dev/ttyACM0', timeout=1) as plc:
    result = plc.read_discrete_inputs(0, 6, unit=0x01)
    print("Input: RunProcess = ", result.bits[0])
    print("Input: EmergencyStop = ", result.bits[5])
    result = plc.read_coils(10, 6, unit=0x01)
    print("Output: RunIntakePump1 = ", result.bits[0])
    print("Output: RunIntakePump2 = ", result.bits[1])
    print("Output: RunIntakePump3 = ", result.bits[2])
    print("Output: RunMixer = ", result.bits[3])
    print("Output: RunOuttakePump = ", result.bits[4])
    print("Output: EmergencyFlush = ", result.bits[5])
    result = plc.read_holding_registers(0, 3, unit=0x01)
    print("Holding Register: State = ", result.registers[0])
    print("Holding Register: Timer = ", result.registers[1])

