import ujson

class Config:
    def __init__(self, path=None):
        if not path:
            self.path = 'settings.json'
        else:
            self.path = path
        self.read()

    def read(self):
        with open(self.path, 'r') as file_:
            self.data = ujson.load(file_)
    
    def write(self):
        with open(self.path, 'w') as file_:
            file_.write(ujson.dumps(self.data))