from machine import Pin, I2C
import time

from config import Config
import onewire
import sensors.ds18x20
import sensors.bme280
import sensors.hx711

_config = Config()

if 'sensors' in _config.data.keys():

    _ds_config = _config.data['sensors'].get('ds1820', {})
    if _ds_config.get('enabled', False):
        ow = onewire.OneWire(
            Pin(_ds_config['pin']))
        i = 0
        while (i < 3 and not ow.roms):
            time.sleep(100)
            ow.scan()
            time.sleep_ms(400)
            i += 1
        if not ow.roms:
            print("No DS1820 found. Is it connected properly?")
        ds1820 = sensors.ds18x20.DS18X20(ow)
    else:
        ds1820 = None

    _hx_config =  _config.data['sensors'].get('hx711', {})
    if _hx_config.get('enabled', False):
        hx711 = sensors.hx711.HX711(
            _hx_config['pin_dout'],
            _hx_config['pin_pdsck']
        )
    else:
        hx711 = None

    _bme_config = _config.data['sensors'].get('bme280', {})
    if _bme_config.get('enabled', False):
        try:
            i2c = I2C(0, I2C.MASTER, pins=(
                _bme_config['pin_sda'],
                _bme_config['pin_scl']
            ))
            bme280 = sensors.bme280.BME280(address=0x77, i2c=i2c)
        except:
            print("BME280 initialization failed. Is it connected properly?")
    else:
        bme280 = None
