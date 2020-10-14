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

def run(mission_number, using_video=False):

    if using_video:
        capture = cv2.VideoCapture(0)
        capture.set(3, 1280)
        capture.set(4, 720)

    cv2.namedWindow("Trackbar")

    # Now create 6 trackbars that will control the lower and upper range of
    # H,S and V channels. The Arguments are like this: Name of trackbar,
    # window name, range,callback function. For Hue the range is 0-179 and
    # for S,V its 0-255.
    cv2.createTrackbar("H lower", "Trackbar", 0, 179, nothing)
    cv2.createTrackbar("S lower", "Trackbar", 0, 255, nothing)
    cv2.createTrackbar("V lower", "Trackbar", 0, 255, nothing)
    cv2.createTrackbar("H upper", "Trackbar", 179, 179, nothing)
    cv2.createTrackbar("S upper", "Trackbar", 255, 255, nothing)
    cv2.createTrackbar("V upper", "Trackbar", 255, 255, nothing)

    if not using_video:
        frame = np.load(get_mission_file_path(mission_number) + 'aligned_image.npy')
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    while True:

        if using_video:
            ret, frame = capture.read()
            if not ret:
                break
            # Flip the frame horizontally (Not required)
            frame = cv2.flip(frame, 1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        l_h = cv2.getTrackbarPos("H lower", "Trackbar")
        l_s = cv2.getTrackbarPos("S lower", "Trackbar")
        l_v = cv2.getTrackbarPos("V lower", "Trackbar")
        u_h = cv2.getTrackbarPos("H upper", "Trackbar")
        u_s = cv2.getTrackbarPos("S upper", "Trackbar")
        u_v = cv2.getTrackbarPos("V upper", "Trackbar")

        lower_range = np.array([l_h, l_s, l_v])
        upper_range = np.array([u_h, u_s, u_v])

        mask = cv2.inRange(hsv, lower_range, upper_range)

        masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
        masked_hsv = cv2.bitwise_and(hsv, hsv, mask=mask)

        mask_3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) # so it can be stacked

        stacked = np.hstack((frame, hsv, mask_3, masked_frame, masked_hsv))

        # Show this stacked frame at 40% of the size.
        cv2.imshow('Trackbars', cv2.resize(stacked, None, fx=0.6, fy=0.6))

        key = cv2.waitKey(1)
        if key == 27:
            break

        if key == ord('s'):
            limits = [[l_h, l_s, l_v], [u_h, u_s, u_v]]
            print(limits)

            # np.save('hsv_limits', limits)
            break

    if using_video:
        capture.release()
        cv2.destroyAllWindows()

if __name__=='__main__':
    if len(sys.argv) != 2:
        sys.exit('[Error] Include Mission #')
    else:
        mission_number = int(sys.argv[1])
        print('Mission #%d' % (mission_number))

    run(mission_number=mission_number, using_video=False)