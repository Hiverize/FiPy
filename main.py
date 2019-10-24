import binascii
import gc
import logger
import machine
import micropython
import network
import pycom
import sys
import time
import uos

import webserver
from config import Config
from sensors import ds1820, hx711, bme280
from wlanmanager import WLanManager


def log(message):
    print(message)


reset_causes = {
    machine.PWRON_RESET: 'PWRON', # Press reset button on FiPy
    machine.HARD_RESET: 'HARD',
    machine.WDT_RESET: 'WDT', # Upload and restart from USB or machine.reset()
    machine.DEEPSLEEP_RESET: 'DEEPSLEEP',
    machine.SOFT_RESET: 'SOFT',
    machine.BROWN_OUT_RESET: 'BROWN_OUT'
}

_config = Config()
_ds_positions = {v: k for k, v in
                 _config.get_value('sensors', 'ds1820', 'positions').items()}
_wm = WLanManager()
_wlan = network.WLAN(id=0)

measurement_interval = _config.get_value('general', 'general', 'measurement_interval')

#set up watchdog, on start timeout only after 1min
wdt = machine.WDT(timeout=60*1000)

loop_run = True
cycle = 0 

log(uos.uname())

def start_measurement():
    global cycle, loop_run

    perf = machine.Timer.Chrono()
    pycom.heartbeat(False)
    pycom.rgbled(0x000000)

    # reconfigure watchdog timeout
    wdt.init(timeout=3*measurement_interval*1000)

    #log("Memory dump on startup:")
    #micropython.mem_info(True)

    while loop_run:
        perf.start()

        # Measure all enabled sensors
        data = {}

        # Start DS1820 conversion
        if ds1820 is not None:
            for rom in ds1820.roms:
                ds1820.start_conversion(rom=rom)
        ms_conversion_start = perf.read_ms()

        # Read data from BME280
        if bme280 is not None:
            try:
                (data['t'],
                data['p'],
                data['h']) = bme280.read_compensated_data()
                data['p'] = data['p']/100 # Pa to mBar
            except:
                log("BME280 not measuring.")
        ms_bme_read = perf.read_ms() - ms_conversion_start

        # Read data from HX711
        if hx711 is not None:
            data['weight_kg'] = hx711.get_value(times=1)
        ms_hx_read = perf.read_ms() - ms_bme_read

        # Read data from DS1820
        if ds1820 is not None and ds1820.roms:
            ms_to_conversion = 750 - perf.read_ms()
            if ms_to_conversion > 0:
                time.sleep_ms(int(ms_to_conversion))
            for rom in ds1820.roms:
                try:
                    ds_measurement = ds1820.read_temp_async(rom=rom)
                    ds_name = binascii.hexlify(rom).decode('utf-8')
                    if ds_name in _ds_positions:
                        data[_ds_positions[ds_name]] = ds_measurement
                except:
                    log("Did not find rom.")
        ms_ds_read = perf.read_ms() - ms_hx_read

        # Log measured values
        if (_wlan.mode() == network.WLAN.STA
                and _wlan.isconnected()
                and _beep is not None):
            _beep.add(data)
        log(data)
        ms_log_data = perf.read_ms() - ms_ds_read

        # Collect garbage
        gc.collect()
        micropython.mem_info()
        ms_gc = perf.read_ms() - ms_log_data

        perf.stop()
        time_elapsed = perf.read_ms()
        time_until_measurement = measurement_interval * 1000 - time_elapsed
        perf.reset()
        cycle += 1
        log("#{:d}, Seconds elapsed: {:.3f}s,"
            "time until next measurement: {:.3f}s".format(cycle, 
                                                          time_elapsed/1000,
                                                          time_until_measurement/1000))
        log("DS1820: {:.0f}ms + {:.0f}ms, BME280: {:.0f}ms, HX711: {:.0f}ms "
            "Log: {:.0f}ms, GC: {:.0f}ms".format(ms_conversion_start,
                                             ms_ds_read,
                                             ms_bme_read,
                                             ms_hx_read,
                                             ms_log_data,
                                             ms_gc))

        wdt.feed()

        if time_until_measurement > 0:
            time.sleep_ms(int(time_until_measurement))


def enable_ap(pin=None):
    global _wm, loop_run, _wlan
    print("Called. Pin {}.".format(pin))
    if not _wlan.mode == network.WLAN.AP:
        log("enabled ap")
        pycom.heartbeat(False)
        pycom.rgbled(0x111100)
        loop_run = False
        getattr(_wm, 'enable_ap')()
    if not webserver.mws.IsStarted():
        webserver.mws.Start(threaded=True)

if _config.get_value('general', 'general', 'button_ap_enabled'):
    button_ap = machine.Pin(_config.get_value('general', 'general', 'button_ap_pin'),
                            mode=machine.Pin.IN,
                            pull=machine.Pin.PULL_UP)
    button_ap.callback(machine.Pin.IRQ_RISING,
                       handler=enable_ap)

# Initial SSID scan
no_ssids = _wm.scan()
log("{:d} SSIDS found".format(no_ssids))

rtc = machine.RTC()
rtc.init(time.gmtime(_config.get_value('general', 'general', 'initial_time')))

log("AP SSID: {}".format(_config.get_value('networking', 'accesspoint', 'ssid')))
log("Cause of restart: {}".format(reset_causes[machine.reset_cause()]))

log("Starting measurement setup...")
wdt.feed()
try:
    if _config.get_value('networking', 'wlan', 'enabled'):
        log("WLan is enabled, trying to connect.")
        _wm.enable_client()
        _beep = logger.beep

        if _wlan.mode() == network.WLAN.STA and _wlan.isconnected():
            try:
                rtc.ntp_sync("pool.ntp.org")
            except:
                pass

            start_measurement()
        else:
            log("No network connection.")
            if ((_config.get_value('networking', 'accesspoint', 'enabled')
                    or _csv is None)
                    and not _config.get_value('general', 'general', 'button_ap_enabled')):
                enable_ap()
            else:
                start_measurement()
    else:
        log("No network connection.")
        _wlan.deinit()
        start_measurement()

except:
    log("Error, dumping memory")
    log(sys.exc_info())
    micropython.mem_info(True)
    #machine.reset()
