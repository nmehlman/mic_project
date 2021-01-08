from smbus2 import SMBus
from time import sleep

def adcReadInit(bus, i2c_addr, slave_addr, adc_ch):

    '''Reads data from ADC.
    \nbus -> SMBus object
    \nslave_addr -> configuration of A0-A2 in string form (i.e. '010')
    \n12c_addr -> hex adress of i2c connection (i.e. 0x12)
    \nadc_ch -> channel where adc is connected (0-3)'''

    addr_byte = '0b1001' + slave_addr + '1'
    control_byte = hex(adc_ch)

    bus.write_byte(i2c_addr, addr_byte)
    bus.write_byte(i2c_addr, addr_byte)
    
def getSample(bus, i2c_addr):
    return bus.read_byte(i2c_addr)
    

bus = SMBus(1)
adcReadInit(bus, 0X48, '000', 0)
while True:
    print(getSample(bus, 0X48))
    sleep(.1)
