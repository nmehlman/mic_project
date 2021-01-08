from smbus2 import SMBus
from time import sleep

def adcReadInit(slave_addr : str, i2c_addr: int, adc_ch: int):

    '''Reads data from ADC.
    \nslave_addr -> configuration of A0-A2 in string form (i.e. '010')
    \n12c_addr -> hex adress of i2c connection (i.e. 0x12)
    \nadc_ch -> channel where adc is connected (0-3)'''

    address = 0x48
    A0 = 0x40
    A1 = 0x41
    A2 = 0x42
    A3 = 0x43
    bus = SMBus(1)
    while True:
        bus.write_byte(address,A0)
        value = bus.read_byte(address)
        print("AOUT:%1.3f  " %(value*3.3/255))
        sleep(0.1)
   

adcReadInit(1,1,1)
