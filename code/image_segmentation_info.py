REGION_NAMES = ['GRASS', 'SIDEWALK', 'BUILDING', 'GRAVEL']

CROP = 10
BORDER_W = 50
BORDER_H = 50

PRECROP = True
SAVE_BORDERED_IMAGE = True

SELECT_REGIONS = True
SELECT_SAMPLES = True
SELECT_LANDMARKS = True

SAVE_REGIONS = True
SAVE_SAMPLES = True
SAVE_LANDMARKS = True

def get_mission_file_path(mission_number):
    return '..\\missions\\mission_' + str(mission_number) + '\\mission_' + str(mission_number) + '_'


def get_mission_segmentation_file_path(mission_number):
    return '..\\missions\\mission_' + str(mission_number) + '_segmentation\\mission_' + str(mission_number) + '_'
