import machine
import pycom
import time
import gc


###############################################################################
# Disable automatic garbage collection                                        #
###############################################################################

gc.disable()

###############################################################################
# Disable LTE modem                                                           #
###############################################################################

if pycom.lte_modem_en_on_boot():
    print("Disabling LTE modem.")
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
# Disable automatic start of WLan device                                      #
###############################################################################

if not pycom.wifi_on_boot():
    pycom.wifi_on_boot(True)

###############################################################################
# Finished boot process                                                       #
###############################################################################

print("Boot finished.")
