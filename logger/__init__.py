from logger.beep import Beep
from logger.csv import CSV_logger
from config import Config

_config = Config()

try:
    beep = Beep(_config)
except:
    beep = None

try:
    csv = CSV_logger()
except OSError:
    csv = None
    print("CSV Logger failed. Is a SD card inserted?")