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
    maxval = 0
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
                    if maxval < houghSpace[math.floor(rho), i]:
                        maxval = houghSpace[math.floor(rho), i] 
    return houghSpace, maxval
def getSides(houghSpace, threshold, angleConst = 20, rhoConst = 20):
    def getVal(rowcol):
        return houghSpace[rowcol[0], rowcol[1]]
    houghRows, houghCols = houghSpace.shape
    angleErr = houghCols / angleConst #raise exception when error < 1
    rhoErr = houghRows / 2 / rhoConst
    sides = list()
    count = 0
    for col in range(houghCols):
        for row in range(houghRows):
            value = houghSpace[row, col]
            if value >= threshold:
                isNew = True
                for i in range(count):
                    if abs(row - sides[i][0]) < rhoErr and abs(col - sides[i][1]) < angleErr:
                        isNew = False
                        break
                if isNew == True:
                    sides.append((row, col))
                    count += 1
                else:
                    if houghSpace[sides[i][0], sides[i][1]] < value:
                        houghSpace[sides[i][0], sides[i][1]] = value
    sides.sort(key = getVal)
    return np.array(sides[0:4]) #raise exception when len < 4
def getCorners(sides, houghSpace):
    houghRows, houghCols = houghSpace.shape
    def getRho(r):
        if r <= houghRows / 2:
            return r
        else:
            return - (houghRows / 2 - (r - houghRows / 2) + 1)
    corners = np.zeros((4,2))
    topLeft, topRight, bottomRight, bottomLeft = getOrderPoints(sides)
    pairs = [(topLeft, topRight), (topLeft, bottomRight), (topRight, bottomLeft), (bottomLeft, bottomRight)]
    i = 0
    for pair in pairs:
        theta1 = pair[0][1] / houghCols * math.pi
        theta2 = pair[1][1] / houghCols * math.pi
        rho1 = getRho(pair[0][0])
        rho2 = getRho(pair[1][0])
        A = np.array([[math.cos(theta1), math.sin(theta1)],
                    [math.cos(theta2), math.sin(theta2)]])
        B = np.array([rho1, rho2]) 
        corners[i] = np.linalg.solve(A, B)
        i += 1
    return corners
def changeView(originalImg, Q = 3):
    ratio = 500 / originalImg.shape[1]
    img = cv.resize(originalImg, None, fx = ratio, fy = ratio, interpolation = cv.INTER_AREA) 
    #inp image should have width <= 500px
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ksize = (5,5)
    blur = cv.GaussianBlur(gray, ksize, 0)
    threshold1 = 50
    threshold2 = 200
    edges = cv.Canny(blur, threshold1, threshold2)
    houghSpace, maxval = houghTransform(edges)
    sides = getSides(houghSpace, maxval / Q)
    corners = getCorners(sides, houghSpace)
    print(corners)
    topLeft, topRight, bottomRight, bottomLeft = getOrderPoints(corners)
    #debug
    '''
    cv.circle(img, tuple(topLeft.astype(int)), 10, (0,255,0), 3)
    cv.circle(img, tuple(topRight.astype(int)), 10, (0,255,0), 3)
    cv.circle(img, tuple(bottomRight.astype(int)), 10, (0,255,0), 3)
    cv.circle(img, tuple(bottomLeft.astype(int)), 10, (0,255,0), 3)
    cv.imwrite('./output/corners.png', img)
    '''
    #end debug
    oldCorners = np.array([topLeft, topRight, bottomRight, bottomLeft], dtype = "float32")
    #Compute new width and height
    newWidth = int(max(getDistance(topLeft, topRight), getDistance(bottomLeft, bottomRight)))
    newHeight = int(max(getDistance(topLeft, bottomLeft), getDistance(topRight, bottomRight)))
    #Compute 4 new corners
    newCorners = np.array([
        [0, 0],
        [newWidth - 1, 0],
        [newWidth - 1, newHeight -1],
        [0, newHeight -1]], dtype = "float32")
    #Compute transformation matrix
    transMat = cv.getPerspectiveTransform(oldCorners, newCorners)
    #Transform
    resultImage = cv.warpPerspective(img, transMat, (newWidth, newHeight))
    return resultImage

