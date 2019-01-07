import cv2 as cv
from scipy import stats
import numpy as np
import math
from scipy import ndimage
def getDistance(a,b):
    return np.linalg.norm(a - b)
def getArea(contour):
    return abs(cv.contourArea(contour))
def getOrderPoints(points):
    '''
    Divide points into 2 part: left and right
    sort the points based on x-coordinates
    '''
    sortArgX = np.argsort(points[:,0]) 
    left = np.array([points[x] for x in sortArgX[0:2]])
    right = np.array([points[x] for x in sortArgX[2:4]])
    #point with bigger y is bottomLeft and vice versa
    bottomLeft = left[np.argmax(left[:,1])]
    topLeft = left[np.argmin(left[:,1])]
    #point that is farther from the topLeft is bottomRight
    if getDistance(topLeft, right[0]) > getDistance(topLeft, right[1]):
        bottomRight = right[0]
        topRight = right[1]
    else:
        bottomRight = right[1]
        topRight = right[0]
    return (topLeft, topRight, bottomRight, bottomLeft)
def houghTransform(edges, houghCols = 180):
    imrows, imcols = edges.shape
    houghRows = 2 * math.ceil(math.sqrt((imrows - 1) ** 2 + (imcols - 1) ** 2)) - 1
    angles = np.zeros(houghCols)
    for col in range(houghCols):
        angles[col] = col * math.pi / houghCols
    houghSpace = np.zeros((houghRows, houghCols), np.int_)
    for col in range(imcols):
        for row in range(imrows):
            if edges[row, col] != 0:
                x = col
                y = row
                for i in range(houghCols):
                    theta = angles[i]
                    rho = x * math.cos(theta) + y * math.sin(theta)
                    houghSpace[math.floor(rho), i] += 1
    return houghSpace
def getRho(r, houghRows):
    if r <= houghRows / 2:
        return r
    else:
        return - (houghRows / 2 - (r - houghRows / 2) + 1)
def getCorners(houghSpace, kernel = 21, angleErrors = 30):
    houghRows, houghCols = houghSpace.shape
    maxfilter = ndimage.maximum_filter(houghSpace, kernel)
    minfilter = ndimage.minimum_filter(houghSpace, kernel)
    maxpoints = np.where((maxima == houghSpace) & ~(minima == houghSpace))
    maxpointsVal = houghSpace[maxpoints]
    partition = np.argpartition(maxpointsVal, -4)[np.array([-1,-2,-3,-4])]
    maxpoints = np.array(maxpoints)[:,partition]
    corners = np.zeros((4,2))
    for i in range(4):
        theta1 = maxpoints[1, i] / houghCols * math.pi
        for j in range(i + 1, 4)
            theta2 = maxpoints[1, j] / houghCols * math.pi
            if abs(theta1 - theta2) < angleErrors / 180 * math.pi:
                continue
            rho1 = getRho(maxpoints[0, i], houghRows)
            rho2 = getRho(maxpoints[0, j], houghRows)
            A = np.array([[math.cos(theta1), math.sin(theta1)],
                          [math.cos(theta2), math.sin(theta2)]])
            B = np.array([rho1, rho2]) 
            corners[i] = np.linalg.solve(A, B)
    return corners
def changeView(img):
    #inp image should have width <= 500px
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ksize = (5,5)
    blur = cv.GaussianBlur(gray, ksize, 0)
    threshold1 = 50
    threshold2 = 200
    edges = cv.Canny(blur, threshold1, threshold2)
    houghSpace = houghTransform(edges)
    corners = getCorners(houghSpace)
    points = getOrderPoints(corners)
    

