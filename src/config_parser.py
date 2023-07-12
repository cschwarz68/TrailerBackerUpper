import yaml
def read_config(filename):
    with open(f'{filename}.yml','r') as f:
        output = yaml.safe_load(f)
    return output
    
#reads yaml file
config = read_config('./src/config')

calibrations = config['settings']

driving = calibrations['driving']

steering = calibrations['steering rack']

camera = calibrations['camera']

streaming = calibrations['streaming']

# TODO: Incorporate this file and constants.py into one file

