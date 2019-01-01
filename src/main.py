import cv2 as cv
import numpy as np
import sys

inp = sys.argv[1]
img = cv.imread(inp)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
edges = cv.Canny(gray, 100, 200)
cv.imwrite('canny.png', edges)
cv.imwrite('original.png', img)
im2 , contours, hierarchy  = cv.findContours(edges, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
res = list()
error = 0.05
minarea = img.shape[0] * img.shape[1] / 2
while True:
    for contour in contours:
        epsilon = error * cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, epsilon, True)
        if len(approx) == 4 and abs(cv.contourArea(approx)) > minarea: 
            res.append(approx)
    if len(res) > 0:
        res = max(res, key = cv.contourArea)
        cv.drawContours(img, [res], -1, (0,255,0), 3) 
        break
    error += 0.05
    if error > 1:
        break
cv.imwrite('contours.png', img)
