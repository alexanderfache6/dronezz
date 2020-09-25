import copy
import cv2
import numpy as np
from matplotlib.path import Path

from manual_image_segmentation_info import *

class RegionSelector():

    def __init__(self, mission_number):
        self.__mission_number = mission_number
        self.__image = None
        self.__original_bordered_image = None
        self.__selected_corners = []
        self.__window_scale_factor = 6
        self.__NUM_REGIONS = 0

    def __select_corners(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.circle(self.__image, (x, y), 20, (0, 0, 255), -1)
            self.__selected_corners.append((x, y))
            print('Corner (%d, %d)' % (x, y))

    def __create_image_window(self, name, image):
        h, w = image.shape[:2]
        h_window = int(round(h / self.__window_scale_factor))
        w_window = int(round(w / self.__window_scale_factor))
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(name, (w_window, h_window))

    def create_image_border(self, image):
        h, w = image.shape[:2]
        bordered_image = np.zeros((h+2*BORDER_H, w+2*BORDER_W, 3)).astype(np.uint8)
        bordered_image[BORDER_H:h+BORDER_H, BORDER_W:w+BORDER_W] = image.astype(np.uint8)

        self.__create_image_window('Bordered Image', bordered_image)
        cv2.imshow('Bordered Image', bordered_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if SAVE_BORDERED_IMAGE:
            print('Saving Bordered Image')
            # np.save(PATH + '\\mission_%d_bordered.npy' % (self.__mission_number), bordered_image)
            cv2.imwrite('mission_'+str(self.__mission_number)+'\\mission_%d_bordered.png' % (self.__mission_number), bordered_image)

        return bordered_image

    def select_regions(self, image_path, region_names):
        self.__image = self.create_image_border(cv2.imread(image_path)) # TODO add black border around to ensure entire area is selected, then just crop out
        self.__original_bordered_image = copy.deepcopy(self.__image) # used to reset window

        self.__NUM_REGIONS = len(region_names)

        num_polygons_per_region = np.zeros((self.__NUM_REGIONS)).astype(int)
        go_to_next_region = False

        all_polygons = []

        #---------- select polygons/subregions for each region

        print('\n---------- Selecting Regions ----------\n')

        for i in range(0, self.__NUM_REGIONS):
            print('Region %d: %s' % (i+1, region_names[i]))

            self.__selected_corners = []

            # create/resize window

            self.__create_image_window('Select Regions', self.__original_bordered_image)
            cv2.setMouseCallback('Select Regions', self.__select_corners)

            # monitor user input
            while True:
                key = cv2.waitKey(1) & 0xFF

                if key == ord('p'): # create polygon
                    self.__selected_corners = np.array(self.__selected_corners).astype(np.int32)
                    cv2.polylines(self.__image, [self.__selected_corners], isClosed=True, color=(255, 0, 0), thickness=15)
                elif key == ord('r'): # reset current polygon
                    self.__selected_corners = []
                    self.__image = copy.deepcopy(self.__original_bordered_image)
                elif key == ord('s'): # save current polygon
                    if len(self.__selected_corners) >= 3:
                        num_polygons_per_region[i] += 1
                        all_polygons.append(self.__selected_corners)
                        self.__selected_corners = []
                        self.__image = copy.deepcopy(self.__original_bordered_image)
                    else:
                        print('not enough corners selected')
                elif key == ord('n'): # go to next region
                    go_to_next_region = True

                cv2.imshow('Select Regions', self.__image) # used in case of reset

                if go_to_next_region:
                    go_to_next_region = False
                    break

            print('Current number of polygons per region:', num_polygons_per_region)

        cv2.destroyAllWindows()
        self.compute_masks(region_names, all_polygons, num_polygons_per_region)

    def compute_masks(self, region_names, all_polygons, num_polygons_per_region):
        #---------- put polygons from some region together in mask

        print('\n---------- Mask Computation ----------\n')

        region_masks = []

        h, w = self.__image.shape[:2]

        for i in range(0, self.__NUM_REGIONS):
            print('Region %d: %s' % (i+1, region_names[i]))
            x, y = np.meshgrid(np.arange(w), np.arange(h))
            points = np.vstack((x.flatten(), y.flatten())).T

            mask = np.zeros((h, w)).astype(int) #0/1
            for j in range(0, num_polygons_per_region[i]):
                print('Polygon %d' % (j+1))
                path = Path(all_polygons[sum(num_polygons_per_region[0:i]) + j])
                grid = path.contains_points(points)
                grid = grid.reshape(h, w).astype(int)

                # add current polygon to region mask
                mask = cv2.bitwise_or(mask, grid)

            region_masks.append(mask)

        if SAVE_MASKS:
            # save region masks
            for i in range(0, self.__NUM_REGIONS):
                np.save('mission_'+str(self.__mission_number)+'\\mission_%d_region_%s.npy' % (self.__mission_number, region_names[i]), region_masks[i])

        #----------

def run(mission_number, image_path, region_names):
    regionSelector = RegionSelector(mission_number)
    regionSelector.select_regions(image_path, region_names)
    print('done')

if __name__=='__main__':
    mission_number = 2
    image_path = '..\\Missions\\mission_'+str(mission_number)+'_composite_3.tiff'

    run(mission_number, image_path, REGION_NAMES)