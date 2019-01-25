import configparser
import os , sys

def get_address(section):
    config = configparser.ConfigParser()
    config.read(os.path.join(sys.path[0],r'config.ini'))
    return (config.get(section=section, option='host'),
            int(config.get(section=section, option='port')))