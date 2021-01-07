from smbus2 import SMBus
from time import sleep

def adcRead(slave_addr, i2c_addr):
    addr_data = '0b' + '1001' + slave_addr + '1'
    addr_data_int = int(addr_data, 2)
    control_data = '0b00000100'
    control_data_int = int(control_data, 2)
    with SMBus(1) as bus:    
        bus.write_byte_data(i2c_addr, 0, addr_data_int)
        bus.write_byte_data(i2c_addr, 0, control_data_int)
    with SMBus(1) as bus: 
        pass#data = bus.read_bus_data(i2c_addr, 0)
    return data

while True:
    print(adcRead('000', 48))
    sleep(.1)


