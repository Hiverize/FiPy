from machine import Pin, I2C
import time
import binascii

from config import Config
#import onewire
#import sensors.ds18x20
from lib.onewire     import OneWire
from sensors.ds18x20 import DS18X20
from sensors.bme280 import BME280
from sensors.hx711 import HX711

_config = Config()

print("init sensors")
# DS18B20 new
if _config.get_value('sensors', 'ds1820', 'enabled'):
    owPin  = _config.get_value('sensors', 'ds1820', 'pin')
    ow     = OneWire(Pin(owPin))
    ds1820 = DS18X20(ow)
    roms   = ds1820.roms
    if not roms:
        print("No DS1820 found. Is it connected properly?")
    else:
        print("Found {} DS1820.".format(len(roms)))
        ds1820.convert_temp()
        time.sleep_ms(750)
    # """ Testausdruck """
    # print('   DS18B20: ', end=' ')
    # for rom in roms:
    #     # print(rom)
    #     name = binascii.hexlify(rom).decode('utf-8')
    #     print( name, end=' ')
    #     tmp = ds1820.read_temp(rom)
    #     if tmp is not None:
    #         ds18b20tmp = int(tmp*10)/10
    #     else:
    #         ds18b20tmp =  999999
    #     print(ds18b20tmp, end=' ')
    # print(' ')
    # if not roms:
    #     print('keine DS18B20 gefunden')
    # else:
    #     print('   DS18B20:', len(roms), ' mal gefunden')
else:
    ds1820 = None

#old
#if _config.get_value('sensors', 'ds1820', 'enabled'):
#    ow = onewire.OneWire(
#        Pin(_config.get_value('sensors', 'ds1820', 'pin')))
#    ds1820 = sensors.ds18x20.DS18X20(ow)
#    time.sleep_ms(200)
#    i = 0
#    while (i < 3 and len(ds1820.roms) < 6):
#        time.sleep_ms(100)
#        ds1820.__init__(ow)
#        time.sleep_ms(400)
#        i += 1
#    if not ds1820.roms:
#        print("No DS1820 found. Is it connected properly?")
#    else:
#        print("Found {} DS1820.".format(len(ds1820.roms)))
#
#else:
#    ds1820 = None

if _config.get_value('sensors', 'hx711', 'enabled'):
    hx711 = HX711(
        _config.get_value('sensors', 'hx711', 'pin_dout'),
        _config.get_value('sensors', 'hx711', 'pin_pdsck')
    )
    hx711.set_scale(_config.get_value('sensors', 'hx711', 'calibration_factor'))
    hx711.set_offset(_config.get_value('sensors', 'hx711', 'tare_offset'))
else:
    hx711 = None

if _config.get_value('sensors','bme280', 'enabled'):
    try:
        i2c = I2C(0, I2C.MASTER, pins=(
            _config.get_value('sensors','bme280', 'pin_sda'),
            _config.get_value('sensors','bme280', 'pin_scl')
        ))
        bme280 = BME280(address=0x77, i2c=i2c)
    except:
        bme280 = None
        print("BME280 initialization failed. Is it connected properly?")
else:
    bme280 = None
