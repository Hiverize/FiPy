import urequests

class Beep:
    def __init__(self, config):
        self.server = config['server']
        self.key = config['sensor_key']

    def add(self, data):
        data['key'] = self.key
        urequests.post(
            '{}/api/sensors'.format(self.server),
            json=data)