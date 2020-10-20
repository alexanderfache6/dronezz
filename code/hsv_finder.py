# https://medium.com/programming-fever/how-to-find-hsv-range-of-an-object-for-computer-vision-applications-254a8eb039fc

import cv2
import numpy as np
import sys
import time

# A required callback method that goes into the trackbar function.
def nothing(x):
    pass

def get_mission_file_path(mission_number):
    return '..\\missions\\mission_' + str(mission_number) + '\\mission_' + str(mission_number) + '_'

def run(mission_number, use_BGR, using_video=False):

    if using_video:
        capture = cv2.VideoCapture(0)
        capture.set(3, 1280)
        capture.set(4, 720)

    cv2.namedWindow("Trackbar")
    cv2.resizeWindow("Trackbar", 1000, 400);

    if use_BGR:
        cv2.createTrackbar("B lower", "Trackbar", 0, 255, nothing)
        cv2.createTrackbar("G lower", "Trackbar", 0, 255, nothing)
        cv2.createTrackbar("R lower", "Trackbar", 0, 255, nothing)
        cv2.createTrackbar("B upper", "Trackbar", 255, 255, nothing)
        cv2.createTrackbar("G upper", "Trackbar", 255, 255, nothing)
        cv2.createTrackbar("R upper", "Trackbar", 255, 255, nothing)
    else:
        cv2.createTrackbar("H lower", "Trackbar", 0, 179, nothing)
        cv2.createTrackbar("S lower", "Trackbar", 0, 255, nothing)
        cv2.createTrackbar("V lower", "Trackbar", 0, 255, nothing)
        cv2.createTrackbar("H upper", "Trackbar", 179, 179, nothing)
        cv2.createTrackbar("S upper", "Trackbar", 255, 255, nothing)
        cv2.createTrackbar("V upper", "Trackbar", 255, 255, nothing)

    if not using_video:
        # frame = np.load(get_mission_file_path(mission_number) + 'aligned_image.npy')
        # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if use_BGR:
            frame = np.load(get_mission_file_path(mission_number) + 'histogram_matched_image.npy')
        else:
            frame = np.load(get_mission_file_path(mission_number) + 'histogram_matched_image_hsv.npy')

    while True:

        if using_video:
            ret, frame = capture.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if use_BGR:
            l_1 = cv2.getTrackbarPos("B lower", "Trackbar")
            l_2 = cv2.getTrackbarPos("G lower", "Trackbar")
            l_3 = cv2.getTrackbarPos("R lower", "Trackbar")
            u_1 = cv2.getTrackbarPos("B upper", "Trackbar")
            u_2 = cv2.getTrackbarPos("G upper", "Trackbar")
            u_3 = cv2.getTrackbarPos("R upper", "Trackbar")
        else:
            l_1 = cv2.getTrackbarPos("H lower", "Trackbar")
            l_2 = cv2.getTrackbarPos("S lower", "Trackbar")
            l_3 = cv2.getTrackbarPos("V lower", "Trackbar")
            u_1 = cv2.getTrackbarPos("H upper", "Trackbar")
            u_2 = cv2.getTrackbarPos("S upper", "Trackbar")
            u_3 = cv2.getTrackbarPos("V upper", "Trackbar")

        lower_range = np.array([l_1, l_2, l_3])
        upper_range = np.array([u_1, u_2, u_3])

        mask = cv2.inRange(frame, lower_range, upper_range)
        masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
        mask_3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) # so it can be stacked

        stacked = np.hstack((frame, mask_3, masked_frame))
        cv2.imshow('Trackbars', cv2.resize(stacked, None, fx=0.8, fy=0.8))

        key = cv2.waitKey(1)
        if key == 27:
            break

        if key == ord('s'):
            print('lower:', [l_1, l_2, l_3])
            print('upper:', [u_1, u_2, u_3])

            # np.save('hsv_limits', limits)
            break

    if using_video:
        capture.release()
        cv2.destroyAllWindows()

if __name__=='__main__':
    if len(sys.argv) != 3:
        sys.exit('[Error] Include Mission # & BGR')
    else:
        mission_number = int(sys.argv[1])
        use_BGR = bool(sys.argv[1])
        print('Mission #%d' % (mission_number))

    run(mission_number=mission_number, use_BGR=use_BGR, using_video=False)