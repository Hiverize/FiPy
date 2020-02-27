from logger.beep import Beep
from logger.csv import CSV_logger
from logger.influx import Influx
from config import Config

_config = Config()

try:
    print("Initialising Beep")
    beep = Beep(_config)
except:
    beep = None
    print("initialising Beep failed")

try:
    print("initialising influx")
    influx = Influx(_config)
except:
    influx = None
    print("initialising influx failed")


try:
    csv = CSV_logger()
except OSError:
    csv = None
    print("CSV Logger failed. Is a SD card inserted?")
