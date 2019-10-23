import binascii
import machine
import network
import time
import sys

from config import Config

class WLanManager():

    def __init__(self):
        self.config = Config()
        self.wlan = network.WLAN()

    def scan(self):
        self.wlan.deinit()
        time.sleep(1)

        # Scan to find all available SSIDs
        self.wlan.init(mode=network.WLAN.STA)
        scan = self.wlan.scan()
        ssids = [{
            'ssid': s.ssid,
            'bssid': binascii.hexlify(s.bssid).decode('utf-8'),
            'sec': s.sec,
            'channel': s.channel} for s in scan]
        self.config.set_value('networking', 'wlan', 'available', ssids)
        self.config.write()
        self.wlan.deinit()
        return len(ssids)

    def configure_antenna(self):
        # https://community.hiveeyes.org/t/signalstarke-des-wlan-reicht-nicht/2541/11
        # https://docs.pycom.io/firmwareapi/pycom/network/wlan/

        antenna_external = self.config.get_value('networking', 'wlan', 'antenna_external')
        print("Using Antenna: ", antenna_external)
        if antenna_external:
            antenna_pin = self.config.get_value('networking', 'wlan', 'antenna_pin')
            print('WiFi: Using external antenna on pin %s', antenna_pin)

            # To use an external antenna, set P12 as output pin.
            from machine import Pin
            Pin(antenna_pin, mode=Pin.OUT)(True)

            # Configure external WiFi antenna.
            self.wlan.antenna(network.WLAN.EXT_ANT)
            print('Antenna set')

        else:
            print('WiFi: Using internal antenna')
            self.wlan.antenna(network.WLAN.INT_ANT)
            print('Antenna set')



    def enable_ap(self):

        # Resolve mode to its numeric code
        mode = network.WLAN.AP

        ssid = self.config.get_value('networking', 'accesspoint', 'ssid')
        password = self.config.get_value('networking', 'accesspoint', 'password')
        encryption = self.config.get_value('networking', 'accesspoint', 'encryption')
        channel = self.config.get_value('networking', 'accesspoint', 'channel')

        try:
            self.wlan.deinit()
            time.sleep(1)
            self.wlan.init(mode=mode,
                           ssid=ssid,
                           auth=(encryption, password),
                           channel=channel)
        except:
            print("WLan restart failed!")
            raise

        try:
            self.wlan.ifconfig(id=1,
                               config=('192.168.4.1',
                                       '255.255.255.0',
                                       '192.168.4.1',
                                       '192.168.4.1'))
        except:
            print("WLan ifconfig failed!")
            raise
        else:
            time.sleep(5)

    def enable_client(self):

        # Resolve mode to its numeric code
        mode = network.WLAN.STA

        ssid = self.config.get_value('networking', 'wlan', 'ssid')
        password = self.config.get_value('networking', 'wlan', 'password')
        encryption = int(self.config.get_value('networking', 'wlan', 'encryption'))

        self.configure_antenna()

        if not (ssid and password):
            print("No WLan connection configured!")
            return

        try:
            self.wlan.deinit()
            time.sleep(1)
            self.wlan.init(mode=mode)
        except:
            print("WLan restart failed!")
            raise


        try:
            ifconfig = self.config.get_value('networking', 'wlan', 'ifconfig')
            if ifconfig == 'static':
                ipaddress = self.config.get_value('networking', 'wlan', 'ipaddress')
                subnet = self.config.get_value('networking', 'wlan', 'subnet')
                gateway = self.config.get_value('networking', 'wlan', 'gateway')
                dns = self.config.get_value('networking', 'wlan', 'dns')

                ip_config = (ipaddress, subnet, gateway, dns)
                self.wlan.ifconfig(id=0, config=ip_config)
            else:
                self.wlan.ifconfig(id=0, config='dhcp')
        except:
            print("WLan ifconfig failed!")
            raise

        try:
            self.wlan.connect(ssid,
                              auth=(encryption, password),
                              timeout=5000)
        except:
            print("WLan connect failed!")
            print("SSID: {}, Enc: {}, PSK: {}".format(ssid,
                                                      encryption,
                                                      password))
            raise
        else:
            time.sleep(5)
