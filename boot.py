import pycom

from wlanmanager import WLanManager
from network import WLAN

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
# Disable automatic start of WLan device                                      #
###############################################################################

if pycom.wifi_on_boot():
    pycom.wifi_on_boot(False)

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
