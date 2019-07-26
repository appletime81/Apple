# coding=UTF-8
# !/usr/bin/python3
import numpy as np
import argparse
import imutils
import cv2
from angle import getAngle
import math
from matplotlib import pyplot as plt

ap = argparse.ArgumentParser()

ap.add_argument("-i", "-image", required=False, help="Path to the image")
ap.add_argument("-s", "-start", required=False, help="auto rotate image which start from the arg")
ap.add_argument("-e", "-end", required=False, help="auto rotate image which end to the arg")
ap.add_argument("-spec", "-spec", required=False, help="auto rotate image to spec angle")

args = vars(ap.parse_args())

test_img = ["image001_ori.jpg"]
start_angle = 0
end_angle = 1


def rotate_img(image, rotate):
    (h, w) = image.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, rotate * (- 1), 1)  # 旋转 , 缩放
    rotation_img = cv2.warpAffine(image, M, (w, h))
    return rotation_img


if args["i"]:
    test_img = [args["i"]]

if args["s"]:
    start_angle = int(args["s"])

if args["e"]:
    end_angle = int(args["e"]) + 1


def auto_rotate_and_test(filename):
    image = cv2.imread(filename)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    if args["spec"]:
        spec_angle = int(args["spec"])
        rotation_img = rotate_img(image, spec_angle)
        calcute_angle(rotation_img, filename, str(spec_angle))
    else:
        for i in range(start_angle, end_angle):
            rotation_img = rotate_img(image, i)
            calcute_angle(rotation_img, filename, str(i))


def calcute_angle(image, filename, angle=""):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (31, 31), 0)
    ret, thresh = cv2.threshold(gray, 30, 200, 0)
    plt.subplot(221)
    plt.imshow(thresh, 'gray')
    if angle != "":
        plt.title("%s auto rotate %s°" % (filename, angle))
    else:
        plt.title("%s" % filename)
    plt.subplot(222)
    plt.imshow(image)
    plt.title("rotation %d°" % (getAngle(image))[0])
    plt.show()


def test_img_list():
    for f in test_img:
        image = cv2.imread(f)
        calcute_angle(image, f)


for img in test_img:
    auto_rotate_and_test(img)
# calcute_angle()
