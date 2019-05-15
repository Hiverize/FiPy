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

_ds_positions = {v: k for k, v in 
                 _config.get_value('sensors', 'ds1820', 'positions').items()}

reset_causes = {
    machine.PWRON_RESET: 'PWRON', # Press reset button on FiPy
    machine.HARD_RESET: 'HARD',
    machine.WDT_RESET: 'WDT', # Upload and restart from USB or machine.reset()
    machine.DEEPSLEEP_RESET: 'DEEPSLEEP',
    machine.SOFT_RESET: 'SOFT',
    machine.BROWN_OUT_RESET: 'BROWN_OUT'
}

loop_run = True

def start_measurement():
    perf = Timer.Chrono()
    global loop_run

    while loop_run:
        perf.start()
        pycom.heartbeat(False)
        pycom.rgbled(0x000000)
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
                    log("Did not find rom")
        if bme280 is not None:
            try:
                (data['t'],
                data['p'],
                data['h']) = bme280.read_compensated_data()
                data['p'] = data['p']/100 # Pa to mBar
            except:
                log("BME280 not measuring.")
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
        log(data)
        perf.stop()
        print('Seconds elapsed: {:.4f}s measurement + {:.4f}s logging'.format(m_time, perf.read()))
        perf.reset()


_wm = WLanManager()

def log(message):
    if _csv is not None:
        _csv.log(message)
    else:
        print(message)

def enable_ap(pin=None):
    global _wm, loop_run, _wlan
    print("Called. Pin {}.".format(pin))
    if not _wlan.mode == network.WLAN.AP:
        log("enabled ap")
        pycom.heartbeat(False)
        pycom.rgbled(0x111100)
        webserver.mws.Start(threaded=True)
        loop_run = False
        getattr(_wm, 'enable_ap')()

if _config.get_value('general', 'general', 'button_ap_enabled'):
    button_ap = machine.Pin(_config.get_value('general', 'general', 'button_ap_pin'),
                            mode=machine.Pin.IN,
                            pull=machine.Pin.PULL_UP)
    button_ap.callback(machine.Pin.IRQ_RISING,
                       handler=enable_ap)


rtc = RTC()
rtc.init(time.gmtime(_config.get_value('general', 'general', 'initial_time')))

_csv  = logger.csv

print("SSID: {}".format(_config.get_value('networking', 'accesspoint', 'ssid')))
log("Cause of restart: {}".format(reset_causes[machine.reset_cause()]))
log("Starting...")
# if the reset cause is not pressing the power button or reconnecting power
if (machine.reset_cause() != 0 or 
        _config.get_value('general', 'general', 'button_ap_enabled')):
    try:
        if _config.get_value('networking', 'wlan', 'enabled'):
            _wm.enable_client()
            if _wlan.mode() == network.WLAN.STA and _wlan.isconnected():
                try:
                    rtc.ntp_sync("pool.ntp.org")
                except:
                    pass
                _beep = logger.beep
                start_measurement()
            else:
                if _config.get_value('networking', 'accesspoint', 'enabled') or _csv is None:
                    enable_ap()
                else:
                    start_measurement()
        else:
            _wlan.deinit()
            start_measurement()
    except OSError:
        print("error. reset machine")
        machine.reset()
    except:
        log("error. reset machine")
        machine.reset()
else: # if the reset cause is pressing the power button or reconnecting power
    enable_ap()
