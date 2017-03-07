import argparse

import cv2
import numpy as np


def calibration(chess_size, images, image_size):
    chess_rows, chess_cols = chess_size
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objp = np.zeros((chess_cols * chess_rows, 3), np.float32)
    objp[:, :2] = np.mgrid[0:chess_cols, 0:chess_rows].T.reshape(-1, 2)
    objpoints, imgpoints = list(), list()

    for image in images:
        ret, corners = cv2.findChessboardCorners(image, chess_size, None)
        cv2.cornerSubPix(image, corners, (11, 11), (-1, -1), criteria)

        objpoints.append(objp)
        imgpoints.append(corners)

    ret, mtx, dist, rvecs, tvecs = \
        cv2.calibrateCamera(objpoints, imgpoints, image_size)

    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        mtx, dist, imageSize=image_size, alpha=1, newImgSize=image_size)

    return mtx, newcameramtx, dist, roi


def save_params(filename, params):
    mtx, newcameramtx, dist, roi = params
    x, y, w, h = roi

    np.savez(filename, x=x, y=y, w=w, h=h, dist=dist,
             newcameramtx=newcameramtx, mtx=mtx)


def read_images(filename):
    images = list()

    with open(filename) as paths:
        for path in paths:
            image = cv2.imread(path)
            # TODO: see docs for read as gray image
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            images.append(gray)

    return images


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--images_file', required=True,
                        help='File with image path collect with collect_images.py')
    parser.add_argument('-o', '--output_params', default='config/undist.npz',
                        help='Output file with undistortion params')
    parser.add_argument('-s', '--chess_size', default='9x6',
                        help='Chess rows and cols in format RxC (9x6 by default)')

    args = parser.parse_args()

    images = read_images(args.images_file)
    if images:
        print 'File not contain paths!'
        exit(-1)

    image_size = images[0].shape[:2]
    chess_rows, chess_cols = args.chess_size.split('x')
    chess_cols = int(chess_cols)
    chess_rows = int(chess_rows)
    chess_size = (chess_rows, chess_cols)

    params = calibration(chess_size, images, image_size)
    save_params(args.output_params, params)
