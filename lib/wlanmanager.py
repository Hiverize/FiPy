import network
from config import Config
import time
import machine
import binascii

class WLanManager():

    def __init__(self):
        self.reload_profiles()
        #self.scan(network.WLAN())

    def reload_profiles(self):
        self.config = Config()
        self.ap_profile = self.config.data['networking']['accesspoint']
        self.client_profile = self.config.data['networking']['wlan']

    def scan(self, wlan):
        # Scan to find all available SSIDs
        wlan.mode(network.WLAN.STA)
        scan = wlan.scan()
        ssids = [{
            'ssid': s.ssid,
            'bssid': binascii.hexlify(s.bssid).decode('utf-8'),
            'sec': s.sec,
            'channel': s.channel} for s in scan]
        self.config.data['networking']['wlan']['available'] = ssids
        self.config.write()

    def enable_ap(self, default=False):
        profile = self.ap_profile
        wlan = network.WLAN()
        wlan.init()
        time.sleep_ms(200)
        self.scan(wlan)
        time.sleep_ms(400)

        # Resolve mode to its numeric code
        mode = network.WLAN.AP

        if default:
            key = 'bienenprojekt'
        else:
            key = profile.get('password', 'bienenprojekt')
        wlan.init(mode=mode,
                  ssid=profile.get('ssid'),
                  auth=(profile.get('encryption', 3),
                        key),
                  channel=profile.get('channel', 1))
        wlan.ifconfig(id=1,
                      config=('10.10.10.1',
                             '255.255.255.0',
                             '10.10.10.1',
                             '10.10.10.1'))
        time.sleep(10)
        if wlan.mode() == 1:
            print('AP creation failed!')
        else:
            print('AP created!')

    def enable_client(self):
        profile = self.client_profile
        wlan = network.WLAN()
        # Resolve mode to its numeric code
        mode = network.WLAN.STA

        wlan.init(mode=mode)
        if profile.get('ifconfig') == 'dhcp':
            wlan.ifconfig(id=0, config='dhcp')
        else:
            ip_config=(profile.get('ipaddress'),
                       profile.get('subnet'),
                       profile.get('gateway'),
                       profile.get('dns'))
            wlan.ifconfig(id=0, config=ip_config)

        wlan.connect(profile.get('ssid'),
                     auth=(profile.get('encryption', 3),
                           profile.get('password')),
                     timeout=1000)
        time.sleep(10)
