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

reset_causes = {
    machine.PWRON_RESET: 'PWRON', # Press reset button on FiPy
    machine.HARD_RESET: 'HARD',
    machine.WDT_RESET: 'WDT', # Upload and restart from USB or machine.reset()
    machine.DEEPSLEEP_RESET: 'DEEPSLEEP',
    machine.SOFT_RESET: 'SOFT',
    machine.BROWN_OUT_RESET: 'BROWN_OUT'
}

print(reset_causes[machine.reset_cause()])