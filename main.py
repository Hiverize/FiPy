import time
from machine import Timer, RTC
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

_config = Config()

_wlan = network.WLAN(id=0)

_ds_config = _config.data['sensors']['ds1820']
_ds_positions = {v: k for k, v in _ds_config['positions'].items()}

loop_run = True

def start_measurement():
    perf = Timer.Chrono()
    global loop_run

    while loop_run:
        pycom.rgbled(0x001100)
        perf.start()
        # Measure all enabled sensors
        data = {}
        if ds1820 is not None:
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
        if bme280 is not None:
            try:
                (data['t'],
                data['p'],
                data['h']) = bme280.read_compensated_data()
                data['p'] = data['p']/100 # Pa to mBar
            except:
                print("BME280 not measuring.")
        if hx711 is not None:
            data['weight_kg'] = hx711.get_value(times=5)
        perf.stop()
        m_time = perf.read()
        perf.reset()

        # Log measured values
        perf.start()
        if _csv is not None:
            _csv.add_dict(data)
        if _wlan.mode() == network.WLAN.STA and _wlan.isconnected() and _beep is not None:
            _beep.add(data)
        print(data)
        perf.stop()
        print('Seconds elapsed: {:.4f}s measurement + {:.4f}s logging'.format(m_time, perf.read()))
        perf.reset()


_wm = WLanManager()

def enable_ap(pin=None):
    global _wm, loop_run
    pycom.heartbeat(False)
    pycom.rgbled(0x111100)
    webserver.mws.Start(threaded=True)
    loop_run = False
    getattr(_wm, 'enable_ap')()

button_s1 = machine.Pin('P10',
                        mode=machine.Pin.IN,
                        pull=machine.Pin.PULL_UP)
button_s1.callback(machine.Pin.IRQ_RISING,
                   handler=enable_ap)


rtc = RTC()
rtc.init(time.gmtime(_config.data['general']['general']['initial_time']//1000))

_csv  = logger.csv
print("Starting...")
if _config.data['networking']['wlan']['enabled']:
    _wm.enable_client()
    if _wlan.mode() == network.WLAN.STA and _wlan.isconnected():
        try:
            rtc.ntp_sync("pool.ntp.org")
        except:
            pass
        _beep = logger.beep
        start_measurement()
    else:
        if _config.data['networking']['accesspoint']['enabled'] or _csv is None:
            enable_ap()
        else:
            start_measurement()
else:
    start_measurement()