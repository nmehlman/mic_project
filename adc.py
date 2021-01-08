from smbus2 import SMBus
from time import sleep

def adcReadInit(slave_addr : str, i2c_addr: int, adc_ch: int):

    '''Reads data from ADC.
    \nslave_addr -> configuration of A0-A2 in string form (i.e. '010')
    \n12c_addr -> hex adress of i2c connection (i.e. 0x12)
    \nadc_ch -> channel where adc is connected (0-3)'''

    address = 0x48
    cmd = 0x40
    value = 0

    bus = SMBus(1)
    while True:
        bus.write_byte_data(address,cmd,value)
        value += 1
        if value == 256:
            value =0
        print("AOUT:%3d" %value)
        sleep(0.01)

adcReadInit('000', 48, 0)
while True:
    print(adcReadInit('000', 48, 0))
    sleep(.1)

