import machine
import pycom
import time

from wlanmanager import WLanManager
from network import WLAN

###############################################################################
# Start of boot.py, flash RGBLED yellow until it is finished                  #
###############################################################################

pycom.heartbeat(False)
pycom.rgbled(0x111100)

print("Boot finished.")

wm = WLanManager()
wm.scan(WLAN())