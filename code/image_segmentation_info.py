REGION_NAMES = ['GRASS', 'SIDEWALK', 'BUILDING', 'GRAVEL']

BORDER = 100

PRECROP = True
SELECT_REGIONS = True
SELECT_SAMPLES = False
SELECT_LANDMARKS = False

SAVE_BORDERED_IMAGE = False
SAVE_REGIONS = False
SAVE_SAMPLES = False
SAVE_LANDMARKS = False

def get_mission_file_path(mission_number):
    return '..\\missions\\mission_' + str(mission_number) + '\\mission_' + str(mission_number) + '_'

def get_mission_segmentation_file_path(mission_number):
    return '..\\missions\\mission_' + str(mission_number) + '_segmentation\\mission_' + str(mission_number) + '_'
