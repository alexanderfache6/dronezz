import copy
import cv2
import imutils
from matplotlib.path import Path
import numpy as np
import os
import sys

# ----------------------------------------

REGION_NAMES = ['GRASS', 'SIDEWALK', 'BUILDING', 'GRAVEL']

BORDER = 100

PRECROP = True
SELECT_REGIONS = True
SELECT_SAMPLES = False
SELECT_LANDMARKS = False

SAVE_BORDERED_IMAGE = True
SAVE_REGIONS = False
SAVE_SAMPLES = False
SAVE_LANDMARKS = False

def get_mission_file_path(mission_number):
    return '..\\missions\\mission_' + str(mission_number) + '\\mission_' + str(mission_number) + '_'

def get_mission_segmentation_file_path(mission_number):
    return '..\\missions\\mission_' + str(mission_number) + '_segmentation\\mission_' + str(mission_number) + '_'

# ----------------------------------------

class ImageSegmentor():

    # ----------------------------------------

    def __init__(self, reference_mission_number, mission_number, image_file_path):
        self.mission_number = mission_number
        self.reference_mission_number = reference_mission_number
        self.image_file_path = image_file_path

        self.current_image = None # image to display in window
        self.current_points = [] # corners user has currently selected

        self.original_image = None # copy used to reset window
        self.bordered_image = None # copy used to reset window
        self.window_scale_factor = 10 # fit window on screen
        self.NUM_REGIONS = len(REGION_NAMES)

    # ----------------------------------------

    def create_image_window(self, window_name, image):
        h, w = image.shape[:2]
        h_window = int(round(h / self.window_scale_factor))
        w_window = int(round(w / self.window_scale_factor))
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.moveWindow(window_name, 20, 20)
        cv2.resizeWindow(window_name, (w_window, h_window))

    def select_points(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.circle(self.current_image, (x, y), 20, param[0], -1)
            self.current_points.append((x, y))
            print('Point (%d, %d)' % (x, y))

    # ----------------------------------------

    def precrop_image(self):
        print('\n---------- Precropping Image ----------\n')
        print('\"left-mouse\" - select point')
        print('\"c\" - create polygon')
        print('\"r\" - reset polygon')
        print('\"s\" - save polygon\n')

        h, w = self.current_image.shape[:2]
        self.bordered_image = np.zeros((h+2*BORDER, w+2*BORDER, 3)).astype(np.uint8)
        self.bordered_image[BORDER:h+BORDER, BORDER:w+BORDER] = self.current_image.astype(np.uint8)

        self.current_image = copy.deepcopy(self.bordered_image)

        self.create_image_window('Precrop Image', self.current_image)
        cv2.setMouseCallback('Precrop Image', self.select_points, [(255, 0, 255)])
        cv2.imshow('Precrop Image', self.current_image)

        self.current_points = [] # clear

        while True:
            cv2.imshow('Precrop Image', self.current_image)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('c'):
                self.current_points = np.array(self.current_points).astype(np.int32)
                cv2.rectangle(self.current_image, pt1=tuple(self.current_points[0]), pt2=tuple(self.current_points[1]), color=(123, 0, 123), thickness=15)
            elif key == ord('r'):
                self.current_points = []
                self.current_image = copy.deepcopy(self.bordered_image)
            elif key == ord('s'):
                self.current_image = copy.deepcopy(self.bordered_image)
                if len(self.current_points) == 2:
                    break
                else:
                    print('must select 2 points - reset')
                    self.current_points = []

        cv2.destroyAllWindows()

        c1 = np.min([self.current_points[0][0], self.current_points[1][0]])
        c2 = np.max([self.current_points[0][0], self.current_points[1][0]])

        r1 = np.min([self.current_points[0][1], self.current_points[1][1]])
        r2 = np.max([self.current_points[0][1], self.current_points[1][1]])

        self.current_image = self.current_image[r1:r2, c1:c2, :]

    def create_bordered_image(self):
        print('\n---------- Creating Bordered Image ----------\n')
        print('Press any key to close')

        h, w = self.current_image.shape[:2]
        self.bordered_image = np.zeros((h+2*BORDER, w+2*BORDER, 3)).astype(np.uint8)
        self.bordered_image[BORDER:h+BORDER, BORDER:w+BORDER] = self.current_image.astype(np.uint8)

        self.create_image_window('Bordered Image', self.bordered_image)
        cv2.imshow('Bordered Image', self.bordered_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if SAVE_BORDERED_IMAGE:
            print('\nSaving Bordered Image')
            print(self.bordered_image.shape)
            cv2.imwrite(get_mission_segmentation_file_path(self.mission_number) + 'bordered.png', self.bordered_image)

    # ----------------------------------------

    def select_regions(self, all_polygons, num_polygons_per_region):
        print('\n---------- Selecting Regions ----------\n')
        print('\"left-mouse\" - select point')
        print('\"c\" - create polygon')
        print('\"r\" - reset polygon')
        print('\"s\" - save polygon')
        print('\"n\" - go to next region\n')

        self.current_image = copy.deepcopy(self.bordered_image)

        go_to_next_region = False

        for i in range(0, self.NUM_REGIONS):
            print('Region %d: %s' % (i+1, REGION_NAMES[i]))

            self.create_image_window('Select Regions', self.current_image)
            cv2.setMouseCallback('Select Regions', self.select_points, [(0, 0, 255)])

            self.current_points = [] # clear

            # monitor user input
            while True:
                cv2.imshow('Select Regions', self.current_image)

                key = cv2.waitKey(1) & 0xFF

                if key == ord('c'): # create polygon
                    self.current_points = np.array(self.current_points).astype(np.int32)
                    cv2.polylines(self.current_image, [self.current_points], isClosed=True, color=(255, 0, 0), thickness=15)
                elif key == ord('r'): # reset current polygon
                    self.current_points = []
                    self.current_image = copy.deepcopy(self.bordered_image)
                elif key == ord('s'): # save current polygon
                    if len(self.current_points) >= 3: # need 3 points to create a polygon area
                        num_polygons_per_region[i] += 1
                        all_polygons.append(self.current_points)
                        self.current_points = []
                        self.current_image = copy.deepcopy(self.bordered_image)
                    else:
                        print('not enough corners selected')
                elif key == ord('n'): # go to next region
                    go_to_next_region = True
                    self.current_image = copy.deepcopy(self.bordered_image)

                if go_to_next_region:
                    go_to_next_region = False
                    break

            print('\nCurrent number of polygons per region:', num_polygons_per_region, '\n')

        cv2.destroyAllWindows()

    def compute_and_save_region_masks(self, all_polygons, num_polygons_per_region):
        print('---------- Computing and Saving Region Masks ----------')

        h, w = self.bordered_image.shape[:2]

        for i in range(0, self.NUM_REGIONS):
            print('\nRegion %d: %s' % (i+1, REGION_NAMES[i]))
            x, y = np.meshgrid(np.arange(w), np.arange(h))
            points = np.vstack((x.flatten(), y.flatten())).T

            region_mask = np.zeros((h, w)).astype(int) #0/1
            for j in range(0, num_polygons_per_region[i]):
                print('Polygon %d' % (j+1))
                path = Path(all_polygons[sum(num_polygons_per_region[0:i]) + j])
                grid = path.contains_points(points)
                grid = grid.reshape(h, w).astype(int)

                # add current polygon to region mask
                region_mask = cv2.bitwise_or(region_mask, grid)

            print(region_mask.shape)
            np.save(get_mission_segmentation_file_path(self.mission_number) + 'region_mask_%s.npy' % (REGION_NAMES[i]), region_mask)

    # ----------------------------------------

    def select_samples(self, all_samples):
        print('\n---------- Selecting Samples ----------')

        self.current_image = copy.deepcopy(self.bordered_image)

        go_to_next_region = False

        for i in range(0, self.NUM_REGIONS):
            print('\nRegion %d: %s' % (i+1, REGION_NAMES[i]))

            self.create_image_window('Select Samples', self.current_image)
            cv2.setMouseCallback('Select Samples', self.select_points, [(0, 0, 255)])

            self.current_points = []

            # monitor user input
            while True:
                cv2.imshow('Select Samples', self.current_image)

                key = cv2.waitKey(1) & 0xFF

                if key == ord('c'): # create polygon
                    self.current_points = np.array(self.current_points).astype(np.int32)
                    cv2.polylines(self.current_image, [self.current_points], isClosed=True, color=(255, 0, 0), thickness=15)
                elif key == ord('r'): # reset current sample
                    self.current_points = []
                    self.current_image = copy.deepcopy(self.bordered_image)
                elif key == ord('s'): # save current polygon
                    if len(self.current_points) >= 3: # need 3 points to create a polygon area
                        all_samples.append(self.current_points)
                        self.current_points = []
                        self.current_image = copy.deepcopy(self.bordered_image)
                    else:
                        print('not enough corners selected')
                elif key == ord('n'): # go to next region
                    go_to_next_region = True
                    self.current_image = copy.deepcopy(self.bordered_image)

                if go_to_next_region:
                    go_to_next_region = False
                    break

        cv2.destroyAllWindows()

    def compute_and_save_samples(self, all_samples):
        print('\n---------- Computing and Saving Sample Masks ----------')

        h, w = self.bordered_image.shape[:2]

        for i in range(0, self.NUM_REGIONS):
            print('\nRegion %d: %s' % (i+1, REGION_NAMES[i]))
            x, y = np.meshgrid(np.arange(w), np.arange(h))
            points = np.vstack((x.flatten(), y.flatten())).T

            sample_mask = np.zeros((h, w)).astype(int) #0/1
            path = Path(all_samples[i])
            grid = path.contains_points(points)
            grid = grid.reshape(h, w).astype(int)

            # add current polygon to region mask
            sample_mask = cv2.bitwise_or(sample_mask, grid)

            print(sample_mask.shape)
            np.save(get_mission_segmentation_file_path(self.mission_number) + 'sample_mask_%s.npy' % (REGION_NAMES[i]), sample_mask)

    # ----------------------------------------

    # def select_landmarks(self):
    #     print('\n---------- Selecting Landmarks ----------\n')
    #
    #     self.current_image = copy.deepcopy(self.bordered_image)
    #
    #     self.create_image_window('Landmarks Image', self.current_image)
    #     cv2.setMouseCallback('Landmarks Image', self.select_points, [(0, 255, 0)])
    #     cv2.imshow('Landmarks Image', self.current_image)
    #
    #     self.current_points = [] # clear
    #
    #     while True:
    #         cv2.imshow('Landmarks Image', self.current_image)
    #
    #         key = cv2.waitKey(1) & 0xFF
    #
    #         if key == ord('r'):
    #             self.current_points = []
    #             self.current_image = copy.deepcopy(self.bordered_image)
    #         elif key == ord('s'):
    #             self.current_image = copy.deepcopy(self.bordered_image)
    #             if len(self.current_points) == 3:
    #                 break
    #             else:
    #                 print('must select at 3 landmarks - reset')
    #                 self.current_points = []
    #
    #     cv2.destroyAllWindows()
    #
    #     return self.current_points

    # ----------------------------------------

    def go(self):

        self.original_image = cv2.imread(self.image_file_path)
        self.current_image = copy.deepcopy(self.original_image)

        if PRECROP: # do this in case image is kind of circular
            self.precrop_image()

        self.create_bordered_image()

        if self.mission_number == self.reference_mission_number:

            if SELECT_REGIONS:
                all_polygons = [] # list of lists containing polygons created for each region
                num_polygons_per_region = np.zeros((self.NUM_REGIONS)).astype(int) # keep track for masks

                self.select_regions(all_polygons, num_polygons_per_region)

                if SAVE_REGIONS:
                    self.compute_and_save_region_masks(all_polygons, num_polygons_per_region)

            if SELECT_SAMPLES:
                all_samples = [] # list of lists containing polygons created of each sample for each region

                self.select_samples(all_samples)

                if SAVE_SAMPLES:
                    self.compute_and_save_samples(all_samples)

            # if SELECT_LANDMARKS:
            #     landmarks = self.select_landmarks()
            #
            #     if SAVE_LANDMARKS:
            #         np.save(get_mission_file_path(self.mission_number) + 'landmarks.npy', landmarks)

    # ----------------------------------------

def run(reference_mission_number, mission_number, image_file_path):
    imageSegmentor = ImageSegmentor(reference_mission_number, mission_number, image_file_path)
    imageSegmentor.go()
    print('done')

if __name__=='__main__':

    if len(sys.argv) != 3:
        sys.exit('[Error] Include Reference Mission # & Mission #')
    else:
        reference_mission_number = int(sys.argv[1])
        mission_number = int(sys.argv[2])
        print('Mission #%d' % (mission_number))

    image_file_path = get_mission_segmentation_file_path(mission_number) + 'orthomosaic_FINAL.tiff'

    # check if file exists
    if not os.path.isfile(image_file_path):
        sys.exit('[Error] File not found: %s' % (image_file_path))
    else:
        print('Loading mission image: %s' % (image_file_path))

    run(reference_mission_number, mission_number, image_file_path)

# download mission_#_orthomosaic_FINAL.tiff after 2 compressions and put into missions/mission_#_segmentation directory
