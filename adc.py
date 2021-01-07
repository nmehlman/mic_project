from smbus2 import SMBus
from time import sleep

def adcReadInit(slave_addr : str, i2c_addr: int, adc_ch: int):

    '''Reads data from ADC.
    \nslave_addr -> configuration of A0-A2 in string form (i.e. '010')
    \n12c_addr -> hex adress of i2c connection (i.e. 0x12)
    \nadc_ch -> channel where adc is connected (0-3)'''

    addr_data = '0b' + '1001' + slave_addr + '1'
    addr_data_int = int(addr_data, 2)
    
    control_data = '0b000000' + bin(adc_ch).replace('0b', '') #Assumes non-differential input
    control_data_int = int(control_data, 2)
    
    i2c_addr = int(str(i2c_addr), 16)

    with SMBus(1) as bus:  
        bus.write_byte_data(i2c_addr, 0, addr_data_int) #Adress
        bus.write_byte_data(i2c_addr, 0, control_data_int) #Control

def getSample(i2c_addr: int):

    i2c_addr = int(str(i2c_addr), 16)

    with SMBus(1) as bus:    
        sample = bus.read_byte(i2c_addr, 0)

    return int(str(sample), 8)

adcReadInit('000', 48, 0)
while True:
    print(getSample(48))
    sleep(.1)

