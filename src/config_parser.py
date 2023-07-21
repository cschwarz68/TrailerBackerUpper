# Most amazing and in-depth parser of all time (deserves a nobel prize)

import yaml
def read_yaml(filename):
    with open(f'{filename}.yml','r') as f:
        output = yaml.safe_load(f)
    return output
    

config = read_yaml('./src/config')

calibrations = config['settings']

driving = calibrations['driving']

steering = calibrations['steering rack']

camera = calibrations['camera']

streaming = calibrations['streaming']

# TODO: Incorporate this file and constants.py into one file

