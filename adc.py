from smbus2 import SMBus
from time import sleep

def adcRead(slave_addr, i2c_addr):
    data = '0b' + '1001' + slave_addr + '1'
    data_int = int(data, 2)
    with SMBus(1) as bus:    
        bus.write_byte_data(i2c_addr, 0, data_int)
        data = bus.read_byte_data(i2c_addr, 0)
    return data

while True:
    print(adcRead('000', 48))
    sleep(.1)


