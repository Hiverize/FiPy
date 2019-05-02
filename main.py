import time
from machine import Timer
import machine
import binascii
import uos
import network
import pycom

from sensors import ds1820, hx711, bme280
import logger
import webserver
from wlanmanager import WLanManager

from config import Config
import logger.csv

_wlan = network.WLAN(id=0)

_config = Config()

_ds_config = _config.data['sensors']['ds1820']
_ds_positions = {v: k for k, v in _ds_config['positions'].items()}

def start_measurement():

    perf = Timer.Chrono()
    global _wlan
    # Start CSV logger on SD
    # Pins are Dat0: P8, SCLK: P23, CMD: P4, at least I think so
    # Apparently Pins can not be changed, when using the SD module
    csv_logger = logger.csv.CSV_logger()
    if _config.data['sensors']['hx711']['enabled']:
        print(_config.data['sensors']['hx711'].get('calibration_factor', 1))
        print(_config.data['sensors']['hx711'].get('tare_offset', 0))
        hx711.set_scale(_config.data['sensors']['hx711'].get('calibration_factor', 1))
        hx711.set_offset(_config.data['sensors']['hx711'].get('tare_offset', 0))
    loop_run = True
    while loop_run:
        pycom.rgbled(0x001100)
        perf.start()
        data = {}
        if _config.data['sensors']['ds1820']['enabled']:
            for rom in ds1820.roms:
                ds1820.start_conversion(rom=rom)
            time.sleep_ms(750)
            for rom in ds1820.roms:
                try:
                    ds_measurement = ds1820.read_temp_async(rom=rom)
                    ds_name = binascii.hexlify(rom).decode('utf-8')
                    if ds_name in _ds_positions:
                        data[_ds_positions[ds_name]] = ds_measurement
                except:
                    print("Did not find rom")
        if _config.data['sensors']['bme280']['enabled']:
            try:
                (data['t'],
                data['p'],
                data['h']) = bme280.read_compensated_data()
                data['p'] = data['p']/100 # Pa to mBar
            except:
                print("BME280 not measuring")
        if _config.data['sensors']['hx711']['enabled']:
            data['weight_kg'] = hx711.get_value(times=5)
        perf.stop()
        csv_logger.add_dict(data)
        if _wlan.mode() == network.WLAN.STA and _wlan.isconnected():
            _beep.add(data)
            print(data)
            print('Seconds elapsed: {:.4f}'.format(perf.read()))
            perf.reset()
            time.sleep(5)
        else:
            loop_run = False

if _wlan.mode() == network.WLAN.STA and _wlan.isconnected():
    _beep = logger.beep
    start_measurement()
else:
    wm = WLanManager()
    wm.enable_ap()

pycom.rgbled(0x111100)
webserver.mws.Start(threaded=True)
