import machine
import pycom
import time

from wlanmanager import WLanManager

###############################################################################
# Start of boot.py, flash RGBLED yellow until it is finished                  #
###############################################################################

pycom.heartbeat(False)
pycom.rgbled(0x111100)

###############################################################################
# Set up Button S1 on Ext Board to toggle WLan AP                             #
###############################################################################

wm = WLanManager()
wm.enable_client()

def enable_ap(pin):
    global wm
    getattr(wm, 'enable_ap')()

button_s1 = machine.Pin('P2',
                        mode=machine.Pin.IN,
                        pull=machine.Pin.PULL_UP)
button_s1.callback(machine.Pin.IRQ_RISING,
                   handler=enable_ap)
