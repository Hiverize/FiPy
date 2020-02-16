# python imports
import gc
import logger
import machine
from machine import Pin, I2C
import micropython
import network
import pycom
import sys
import time
import uos

# own code imports
import webserver
from config import Config
from sensors import hx711, bme280
import sensors.ssd1306
from wlanmanager import WLanManager

from lib.onewire     import OneWire
from sensors.ds18x20 import DS18X20



# Log method
def log(message):
    print(message)

# needed for boards without buttons
reset_causes = {
    machine.PWRON_RESET: 'PWRON', # Press reset button on FiPy
    machine.HARD_RESET: 'HARD',
    machine.WDT_RESET: 'WDT', # Upload and restart from USB or machine.reset()
    machine.DEEPSLEEP_RESET: 'DEEPSLEEP',
    machine.SOFT_RESET: 'SOFT',
    machine.BROWN_OUT_RESET: 'BROWN_OUT'
}

# init
_config = Config()
_ds_positions = {v: k for k, v in
                 _config.get_value('sensors', 'ds1820', 'positions').items()}
_wm = WLanManager(_config)
_wlan = network.WLAN(id=0)

measurement_interval = _config.get_value('general', 'general', 'measurement_interval')

#set up watchdog, on start timeout only after 1min
wdt = machine.WDT(timeout=60*1000)

loop_run = True
cycle = 0

oled = _config.get_value('general', 'general', 'oled')
if oled:
    i2c = I2C(0, I2C.MASTER, pins=('P9', 'P10'))       # PyCom FiPy
    _oled = sensors.ssd1306.SSD1306_I2C(128, 64, i2c)           # x, y, bus
    _oled.fill(1)
    _oled.show()

# DS18B20 new
if _config.get_value('sensors', 'ds1820', 'enabled'):
    owPin  = _config.get_value('sensors', 'ds1820', 'pin')
    ow     = OneWire(Pin(owPin))
    ds1820 = DS18X20(ow)
    roms   = ds1820.scan()
else:
    ds1820 = None

log(uos.uname())



# start main measurement cycle
def start_measurement():
    global cycle, loop_run

    perf = machine.Timer.Chrono()
    #pycom.heartbeat(False)
    #pycom.rgbled(0x007f00)

    # reconfigure watchdog timeout
    wdt.init(timeout=3*measurement_interval*1000)

    #log("Memory dump on startup:")
    #micropython.mem_info(True)

    while loop_run:
        # start time measuring
        perf.start()

        # Measure all enabled sensors
        data = {}

        # Start DS1820 conversion
        if ds1820 is not None:
                    ds1820.convert_temp()
                    time.sleep_ms(750)
                    print('   DS18B20: Messung gestartet...')
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
        # if ds1820 is not None and ds1820.roms:
        #     ms_to_conversion = 750 - perf.read_ms()
        #     if ms_to_conversion > 0:
        #         time.sleep_ms(int(ms_to_conversion))
        #     for rom in ds1820.roms:
        #         try:
        #             ds_measurement = ds1820.read_temp_async(rom=rom)
        #             ds_name = binascii.hexlify(rom).decode('utf-8')
        #             if ds_name in _ds_positions:
        #                 data[_ds_positions[ds_name]] = ds_measurement
        #         except:
        #             log("Did not find rom.")
        # ms_ds_read = perf.read_ms() - ms_hx_read
        if ds1820 is not None:
            print('   DS18B20:', end=' ')
            ds_data = ds1820.read_all(_ds_positions)
            data.update(ds_data)
            print(' ')
        ms_ds_read = perf.read_ms() - ms_hx_read

        if oled:
            _oled.fill(0)                                         # alles aus
            #oled.text("BOB     hh:mm:ss",   0,  0)               # Textausgabe
            #oled.text(str(counter),        30,  0)
            _oled.text("Waage           " ,  0,  9)
            if 'weight_kg' in data:
                _oled.text(str(round(data['weight_kg'],1)),       64,  9)
            _oled.text("kg",               100,  9)
            _oled.text("BME280          " ,  0, 18)
            if 't' in data:
                _oled.text(str(round(data['t'],1))     ,  0, 27)
            if 'p' in data:
                _oled.text(str(round(data['p'],1))     , 40, 27)
            if 'h' in data:
                _oled.text(str(round(data['h'],1))     , 95, 27)
            _oled.text("DS18B20         " ,  0, 36)
            if 't_i_1' in data:
                _oled.text(str(round(data['t_i_1'],1)),  0, 45)
            if 't_i_2' in data:
                _oled.text(str(round(data['t_i_2'],1)), 50, 45)
            if 't_i_3' in data:
                _oled.text(str(round(data['t_i_3'],1)), 95, 45)
            if 't_i_4' in data:
                _oled.text(str(round(data['t_i_4'],1)),  0, 54)
            if 't_i_5' in data:
                _oled.text(str(round(data['t_i_5'],1)), 50, 54)
            if 't_o' in data:
                _oled.text(str(round(data['t_o'],1)), 95, 54)
            _oled.show()                                         # anzeigen


        # Log measured values, if possible
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


def ap_already_enabled():
    log("ap already enabled.")

# enable ap
def enable_ap(pin=None):
    global _wm, loop_run, _wlan, wdt, button_ap
    if _config.get_value('general', 'general', 'button_ap_enabled'):
        button_ap.callback(handler=ap_already_enabled)
        print("Called. Pin {}.".format(pin))
    wdt.init(timeout=30*60*1000)
    if not _wlan.mode() == network.WLAN.AP:
        loop_run = False
        getattr(_wm, 'enable_ap')()
        log("enabled ap")
        #pycom.heartbeat(False)
        #pycom.rgbled(0x007f00)
    if not webserver.mws.IsStarted():
        webserver.mws.Start(threaded=True)

###### run this #######

# Initial SSID scan
no_ssids = _wm.scan()
log("{:d} SSIDS found".format(no_ssids))

# init time
try:
    rtc = machine.RTC()
    rtc.init(time.gmtime(_config.get_value('general', 'general', 'initial_time')))
except:
    log("Time init failed")
    rtc.init(time.gmtime(1556805688))

log("AP SSID: {}".format(_config.get_value('networking', 'accesspoint', 'ssid')))
log("Cause of restart: {}".format(reset_causes[machine.reset_cause()]))

log("switching to ap mode is now possible")
pycom.rgbled(0x007f00)
if _config.get_value('general', 'general', 'button_ap_enabled'):
    button_ap = machine.Pin(_config.get_value('general', 'general', 'button_ap_pin'),
                            mode=machine.Pin.IN,
                            pull=machine.Pin.PULL_UP)
    button_ap.callback(machine.Pin.IRQ_RISING,
                       handler=enable_ap)


log("Starting measurement setup...")
wdt.feed()
try:
    if _config.get_value('networking', 'wlan', 'enabled'):
        log("WLan is enabled, trying to connect.")
        _wm.enable_client()
        _beep = logger.beep

        # add to time server
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
        log("Measuring without network connection.")
        _wlan.deinit()
        start_measurement()

except:
    log("Error, dumping memory")
    log(sys.exc_info())
    micropython.mem_info(True)
    #machine.reset()
