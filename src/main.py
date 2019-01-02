import cv2 as cv
import numpy as np
import sys
#resize the image for faster processing
inp = sys.argv[1]
img = cv.imread(inp)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
blur = cv.GaussianBlur(gray, (5,5), 0)
edges = cv.Canny(blur, 50, 200)
#need to improve by automatically decide Canny parameters
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
    cv.drawContours(img, np.array([res]), -1, (0,255,0), 3) 
else:
    print("Contours not found")
cv.imwrite('./output/contours.png', img)
def getDistance(a,b):
    
def getOrderPoints(points):
    #divide points into 2 part: left and right
    #sort the points based on x-coordinates
    sortArgX = np.argsort(points[:,0]) 
    left = np.array([points[x] for x in sortArgX[0:2]])
    right = np.array([points[x] for x in sortArgX[2:4]])
    #point with bigger y is topLeft and vice versa
    topLeft = left[np.argmax(left[:,1])]
    bottomLeft = left[np.argmin(left[:,1])]
    #point that is farther from the topLeft is bottomRight
    if getDistance(topLeft, right[0]) > getDistance(topLeft, right[1]):
        bottomRight = right[0]
        topRight = right[1]
    else:
        bottomRight = right[1]
        topRight = right[0]
