from smbus2 import SMBus
from time import sleep
from time import perf_counter as timer

def adcReadInit(bus, i2c_addr, slave_addr, adc_ch):

    '''Reads data from ADC.
    \nbus -> SMBus object
    \ni2c_addr -> hex adress of i2c connection (i.e. 0x12)
    \nslave_addr -> configuration of A0-A2 in string form (i.e. '010')
    \nadc_ch -> channel where adc is connected (0-3)'''

    addr_byte = '0b1001' + slave_addr + '1'
    addr_byte = int(addr_byte, 2)
    control_byte = adc_ch

    bus.write_byte(i2c_addr, addr_byte)
    bus.write_byte(i2c_addr, control_byte)
    
def getSample(bus, i2c_addr):
    return bus.read_byte(i2c_addr)
    

bus = SMBus(1)
adcReadInit(bus, 0X48, '000', 0)
samples = []

s = timer()
i = 0
while timer() - s < 1:
    sample = bus.read_byte(0x48)
    i+=1
    print("Input level: %s" % sample)

print(i)