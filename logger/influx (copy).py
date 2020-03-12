import urequests
import sys

class Influx:
    def __init__(self, config):
        self.server = config.get_value('telemetry', 'beep', 'server')
        self.failures = 0

    def send(self, file):
        print("Trying to send file.")
        try:
            response = urequests.post(
                'http://134.102.219.159:8086/write?db=bee_data&u=kamerun&p=ngaoundere',
                data=file)
            print("printing response:")
            print(response)
            sent = True
        except:
            self.failures += 1
            print("Error sending data! (Count: {:d})".format(self.failures))
            print(sys.exc_info())
            sent = False
        return sent
