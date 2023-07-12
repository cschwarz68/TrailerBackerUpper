import yaml
def read_one_block_of_yaml_data(filename):
    with open(f'{filename}.yml','r') as f:
        output = yaml.safe_load(f)
    return output
    
#reads yaml file
config = read_one_block_of_yaml_data('/home/nads/Documents/Python/TrailerBackerUpper/src/config')

calibrations = config['calibrations']

driving = calibrations['driving']

steering = calibrations['steering rack']

camera = calibrations['camera']

streaming = calibrations['streaming']

# TODO: Incorporate this file and constants.py into one file

