import network
from config import Config
import time
import machine
import binascii

class WLanManager():

    def __init__(self):
        self.config = Config()

    def scan(self, wlan):
        # Scan to find all available SSIDs
        wlan.init(mode=network.WLAN.STA)
        scan = wlan.scan()
        ssids = [{
            'ssid': s.ssid,
            'bssid': binascii.hexlify(s.bssid).decode('utf-8'),
            'sec': s.sec,
            'channel': s.channel} for s in scan]
        self.config.set_value('networking', 'wlan', 'available', ssids)
        self.config.write()
        return len(ssids)

    def enable_ap(self, default=False):
        wlan = network.WLAN(id=0)

        # Resolve mode to its numeric code
        mode = network.WLAN.AP

        ssid = self.config.get_value('networking', 'accesspoint', 'ssid') 
        password = self.config.get_value('networking', 'accesspoint', 'password')
        encryption = self.config.get_value('networking', 'accesspoint', 'encryption')
        channel = self.config.get_value('networking', 'accesspoint', 'channel')

        wlan.init(mode=mode,
                  ssid=ssid,
                  auth=(encryption, password),
                  channel=channel)
        wlan.ifconfig(id=1,
                      config=('192.168.4.1',
                              '255.255.255.0',
                              '192.168.4.1',
                              '192.168.4.1'))
        time.sleep(10)

    def enable_client(self):
        # Resolve mode to its numeric code
        mode = network.WLAN.STA

        wlan = network.WLAN(mode=mode)
        time.sleep(2)

        ssid = self.config.get_value('networking', 'wlan', 'ssid') 
        password = self.config.get_value('networking', 'wlan', 'password')
        encryption = int(self.config.get_value('networking', 'wlan', 'encryption'))
        wlan.connect(ssid,
                     auth=(encryption, password))
        time.sleep(10)

        # ifconfig = self.config.get_value('networking', 'wlan', 'ifconfig')
        # if ifconfig == 'dhcp':
        #     wlan.ifconfig(config='dhcp')
        # else:
        #     ipaddress = self.config.get_value('networking', 'wlan', 'ipaddress')
        #     subnet = self.config.get_value('networking', 'wlan', 'subnet')
        #     gateway = self.config.get_value('networking', 'wlan', 'gateway')
        #     dns = self.config.get_value('networking', 'wlan', 'dns')
        #     ip_config=(ipaddress, subnet, gateway, dns)
        #     wlan.ifconfig(config=ip_config)
