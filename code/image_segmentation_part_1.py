import copy
import cv2
from matplotlib.path import Path
import numpy as np
import os
import sys

from image_segmentation_info import *

class ImageSegmentor():

    def __init__(self, mission_number, image_path):
        self.mission_number = mission_number
        self.image_path = image_path

        self.current_image = None
        self.original_bordered_image = None # copy used to reset window
        self.current_points = [] # corners user has currently selected
        # self.landmarks = []
        self.window_scale_factor = 6
        self.NUM_REGIONS = len(REGION_NAMES)

    def select_points(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.circle(self.current_image, (x, y), 20, param[0], -1)
            self.current_points.append((x, y))
            print('Point (%d, %d)' % (x, y))

    # X
    def create_image_window(self, window_name, image):
        h, w = image.shape[:2]
        h_window = int(round(h / self.window_scale_factor))
        w_window = int(round(w / self.window_scale_factor))
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, (w_window, h_window))

    # X
    def create_bordered_image(self):
        print('\n---------- Creating Bordered Image ----------\n')

        self.current_image = cv2.imread(image_path)

        h, w = self.current_image.shape[:2]
        bordered_image = np.zeros((h+2*BORDER_H, w+2*BORDER_W, 3)).astype(np.uint8)
        bordered_image[BORDER_H:h+BORDER_H, BORDER_W:w+BORDER_W] = self.current_image.astype(np.uint8)

        print('Press any key to close')

        self.create_image_window('Bordered Image', bordered_image)
        cv2.imshow('Bordered Image', bordered_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if SAVE_BORDERED_IMAGE:
            print('\nSaving Bordered Image')
            cv2.imwrite(get_mission_segmentation_file_path(self.mission_number) + 'bordered.png', bordered_image)

        self.original_bordered_image = copy.deepcopy(bordered_image)

    def select_regions(self, all_polygons, num_polygons_per_region):
        print('\n---------- Selecting Regions ----------\n')

        print('\"left-mouse\" - select point')
        print('\"c\" - create polygon')
        print('\"r\" - reset polygon')
        print('\"s\" - save polygon')
        print('\"n\" - go to next region\n')

        self.current_image = copy.deepcopy(self.original_bordered_image)

        go_to_next_region = False

        for i in range(0, self.NUM_REGIONS):
            print('Region %d: %s' % (i+1, REGION_NAMES[i]))

            self.create_image_window('Select Regions', self.current_image)
            cv2.setMouseCallback('Select Regions', self.select_points, [(0, 0, 255)])

            self.current_points = [] # clear

            # monitor user input
            while True:
                key = cv2.waitKey(1) & 0xFF

                if key == ord('c'): # create polygon
                    self.current_points = np.array(self.current_points).astype(np.int32)
                    cv2.polylines(self.current_image, [self.current_points], isClosed=True, color=(255, 0, 0), thickness=15)
                elif key == ord('r'): # reset current polygon
                    self.current_points = []
                    self.current_image = copy.deepcopy(self.original_bordered_image)
                elif key == ord('s'): # save current polygon
                    if len(self.current_points) >= 3: # need 3 points to create a polygon area
                        num_polygons_per_region[i] += 1
                        all_polygons.append(self.current_points)
                        self.current_points = []
                        self.current_image = copy.deepcopy(self.original_bordered_image)
                    else:
                        print('not enough corners selected')
                elif key == ord('n'): # go to next region
                    go_to_next_region = True
                    self.current_image = copy.deepcopy(self.original_bordered_image)

                cv2.imshow('Select Regions', self.current_image)

                if go_to_next_region:
                    go_to_next_region = False
                    break

            print('\nCurrent number of polygons per region:', num_polygons_per_region, '\n')

        cv2.destroyAllWindows()

    def compute_and_save_region_masks(self, all_polygons, num_polygons_per_region):
        print('---------- Computing and Saving Region Masks ----------')

        h, w = self.current_image.shape[:2]

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

                # add current polygon to region maskW
                region_mask = cv2.bitwise_or(region_mask, grid)

            np.save(get_mission_segmentation_file_path(self.mission_number) + 'region_mask_%s.npy' % (REGION_NAMES[i]), region_mask)

    def select_samples(self, all_samples):
        print('\n---------- Selecting Samples ----------')

        self.current_image = copy.deepcopy(self.original_bordered_image)

        go_to_next_region = False

        for i in range(0, self.NUM_REGIONS):
            print('\nRegion %d: %s' % (i+1, REGION_NAMES[i]))

            self.create_image_window('Select Samples', self.current_image)
            cv2.setMouseCallback('Select Samples', self.select_points, [(0, 0, 255)])

            self.current_points = []

            # monitor user input
            while True:
                key = cv2.waitKey(1) & 0xFF

                if key == ord('c'): # create polygon
                    self.current_points = np.array(self.current_points).astype(np.int32)
                    cv2.polylines(self.current_image, [self.current_points], isClosed=True, color=(255, 0, 0), thickness=15)
                elif key == ord('r'): # reset current sample
                    self.current_points = []
                    self.current_image = copy.deepcopy(self.original_bordered_image)
                elif key == ord('s'): # save current polygon
                    if len(self.current_points) >= 3: # need 3 points to create a polygon area
                        all_samples.append(self.current_points)
                        self.current_points = []
                        self.current_image = copy.deepcopy(self.original_bordered_image)
                    else:
                        print('not enough corners selected')
                elif key == ord('n'): # go to next region
                    go_to_next_region = True
                    self.current_image = copy.deepcopy(self.original_bordered_image)

                cv2.imshow('Select Samples', self.current_image)

                if go_to_next_region:
                    go_to_next_region = False
                    break

        cv2.destroyAllWindows()

    def compute_and_save_samples(self, all_samples):
        print('\n---------- Computing and Saving Sample Masks ----------')

        h, w = self.current_image.shape[:2]

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

            np.save(get_mission_segmentation_file_path(self.mission_number) + 'sample_mask_%s.npy' % (REGION_NAMES[i]), sample_mask)

    def go(self):
        self.create_bordered_image()

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

        if SELECT_LANDMARKS:
            # # select landmarks
            # # self.create_image_window('Select Landmarks', self.original_bordered_image)
            # cv2.setMouseCallback('Select Regions', self.select_points, [(0, 255, 0)]) # TODO not showing color
            #
            # print('Select Landmarks')
            # while True:
            #     key = cv2.waitKey(1) & 0xFF
            #
            #     if key == ord('r'): # reset landmarks
            #         self.current_points = []
            #         self.current_image = copy.deepcopy(self.original_bordered_image)
            #     elif key == ord('s'): # save landmarks
            #         if len(self.current_points) >= 2:
            #             self.landmarks = np.array(self.current_points).astype(np.int32)
            #             break
            #         else:
            #             print('not enough corners selected')
            #
            # print(self.landmarks)
            #
            # cv2.destroyAllWindows()

            if SAVE_LANDMARKS:
                np.save(get_mission_file_path(self.mission_number) + 'landmarks.npy', self.landmarks)

def run(mission_number, image_path):
    imageSegmentor = ImageSegmentor(mission_number, image_path)
    imageSegmentor.go()
    print('done')

if __name__=='__main__':

    # get mission number
    if len(sys.argv) != 2:
        sys.exit('[Error] Include Mission #')
    else:
        mission_number = int(sys.argv[1])
        print('Mission #%d' % (mission_number))

    image_path = get_mission_file_path(mission_number) + 'orthomosaic_FINAL.tiff'

    # check if file exists
    if not os.path.isfile(image_path):
        sys.exit('[Error] File not found: %s' % (image_path))
    else:
        print('Loading mission image: %s' % (image_path))

    run(mission_number, image_path)



# download mission_#_orthomosaic_FINAL.tiff after 2 compressions and put into missions/mission_1 directory
