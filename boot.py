import machine
import pycom
import time
import gc

from wlanmanager import WLanManager
from network import WLAN, LTE

###############################################################################
# Disable automatic garbage collection                                        #
###############################################################################

gc.disable()

###############################################################################
# Disable LTE modem                                                           #
###############################################################################

if pycom.lte_modem_en_on_boot():
    pycom.lte_modem_en_on_boot(False)

###############################################################################
# Disable LED heartbeat on boot                                               #
###############################################################################

if pycom.heartbeat_on_boot():
    pycom.heartbeat_on_boot(False)
    pycom.heartbeat(False)

###############################################################################
# Start of boot.py, yellow LED until it is finished                           #
###############################################################################

print("Starting boot process...")
pycom.rgbled(0x111100)

###############################################################################
# Enable automatic start of WLan device                                      #
###############################################################################

if not pycom.wifi_on_boot():
    pycom.wifi_on_boot(True)

###############################################################################
# Initial scan of available WLan SSIDS                                        #
###############################################################################

wm = WLanManager()
no_ssids = wm.scan(WLAN())
print("{:d} SSIDS found".format(no_ssids))

###############################################################################
# Finished boot process                                                       #
###############################################################################

print("Boot finished.")