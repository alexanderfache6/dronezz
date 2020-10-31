import json
import sys

from image_segmentation_info import *

def run(mission_number):
    metadata = {}

    while True:
        field = input('Field: ')
        if field == 'X':
            break
        value = input('Value: ')

        metadata[field] = value

    with open(get_mission_file_path(mission_number) + 'metadata.json', 'w') as file:
        json.dump(metadata, file)

if __name__=='__main__':

    # get mission number
    if len(sys.argv) != 2:
        sys.exit('[Error] Include Mission #')
    else:
        mission_number = int(sys.argv[1])
        print('Mission #%d' % (mission_number))

    run(mission_number)
