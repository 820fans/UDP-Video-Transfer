import configparser
import os

class Config:
    def __init__(self):
        pass

    def get(self, section, key):
        config = configparser.ConfigParser()
        file_root = os.path.dirname(__file__)
        path = os.path.join(file_root, 'config.conf')
        config.read(path)
        return config.get(section, key)