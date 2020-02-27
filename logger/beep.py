import urequests
import sys

class Beep:
    def __init__(self, config):
        self.server = config.get_value('telemetry', 'beep', 'server')
        self.key = config.get_value('telemetry', 'beep', 'sensor_key')
        self.failures = 0

    def add(self, data):
        data['key'] = self.key
        try:
            urequests.post(
                '{}/api/sensors'.format(self.server),
                json=data)
        except:
            self.failures += 1
            print("Error sending data! (Count: {:d})".format(self.failures))
            print(sys.exc_info())
