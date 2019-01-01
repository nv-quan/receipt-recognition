import cv2 as cv
import numpy as np
import sys

inp = sys.argv[1]
img = cv.imread(inp)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
blur = cv.GaussianBlur(gray, (5,5), 0)
edges = cv.Canny(blur, 50, 200)
cv.imwrite('./output/canny.png', edges)
cv.imwrite('./output/original.png', img)
im2 , contours, hierarchy  = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
res = list()
error = 0.02
# minarea = img.shape[0] * img.shape[1] / 2
for contour in contours:
    epsilon = error * cv.arcLength(contour, True)
    approx = cv.approxPolyDP(contour, epsilon, True)
    if len(approx) == 4:
        res.append(approx)
if len(res) > 0:
    res = max(res, key = cv.contourArea)
    cv.drawContours(img, [res], -1, (0,255,0), 3) 
# print(res)
cv.imwrite('./output/contours.png', img)
