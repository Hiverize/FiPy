import urequests

class Beep:
    def __init__(self, config):
        self.server = config.get_value('telemetry', 'beep', 'server')
        self.key = config.get_value('telemetry', 'beep', 'sensor_key')

    def add(self, data):
        data['key'] = self.key
        urequests.post(
            '{}/api/sensors'.format(self.server),
            json=data)