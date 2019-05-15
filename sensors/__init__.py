from machine import Pin, I2C
import time

from config import Config
import onewire
import sensors.ds18x20
import sensors.bme280
import sensors.hx711

_config = Config()

if _config.get_value('sensors', 'ds1820', 'enabled'):
    ow = onewire.OneWire(
        Pin(_config.get_value('sensors', 'ds1820', 'pin')))
    ds1820 = sensors.ds18x20.DS18X20(ow)
    time.sleep_ms(200)
    i = 0
    while (i < 3 and len(ds1820.roms) < 6):
        time.sleep_ms(100)
        ds1820.__init__(ow)
        time.sleep_ms(400)
        i += 1
    if not ds1820.roms:
        print("No DS1820 found. Is it connected properly?")
    else:
        print("Found {} DS1820.".format(len(ds1820.roms)))

else:
    ds1820 = None

if _config.get_value('sensors', 'hx711', 'enabled'):
    hx711 = sensors.hx711.HX711(
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
        bme280 = sensors.bme280.BME280(address=0x77, i2c=i2c)
    except:
        bme280 = None
        print("BME280 initialization failed. Is it connected properly?")
else:
    bme280 = None
