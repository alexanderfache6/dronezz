REGION_NAMES = ['GRASS', 'SIDEWALK', 'BUILDING', 'GRAVEL']

CROP = 10
BORDER_W = 50
BORDER_H = 50

SAVE_BORDERED_IMAGE = False

SELECT_REGIONS = False
SELECT_SAMPLES = False
SELECT_LANDMARKS = True

SAVE_REGIONS = False
SAVE_SAMPLES = False
SAVE_LANDMARKS = True

def get_mission_segmentation_file_path(mission_number):
    return '..\\missions\\mission_' + str(mission_number) + '_segmentation\\mission_' + str(mission_number) + '_'
