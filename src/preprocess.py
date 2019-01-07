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
def changeView(originalImg, Q = 3):
    def getLength(contour):
        return cv.arcLength(contour, False)
    height = originalImg.shape[0]
    width = originalImg.shape[1]
    img = originalImg
    ratio = 1
    if width > 1000:
        ratio = 500 / width
        img = cv.resize(originalImg, None, fx = ratio, fy = ratio, interpolation = cv.INTER_LINEAR) 
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ksize = (5,5)
    blur = cv.GaussianBlur(gray, ksize, 0)
    threshold1 = 50
    threshold2 = 200
    edges = cv.Canny(blur, threshold1, threshold2)
    contourImg, contours, hierarchy = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    maxcontour = max(contours, key = getLength)
    black = np.zeros((int(height * ratio), int(width * ratio)), "uint8")
    cv.drawContours(black, [maxcontour], -1, (255,255,255), 1)
    dilate = cv.dilate(black, (7,7))
    erode = cv.erode(dilate, (7,7))
    contourImg, contours, hierarchy = cv.findContours(erode, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    maxcontour = max(contours, key = getLength)
    cv.imwrite('./output/erode.png', erode)
    error = 0.1
    epsilon = error * cv.arcLength(maxcontour, True)
    approx = cv.approxPolyDP(maxcontour, epsilon, True)
    cv.cvtColor(black, cv.COLOR_GRAY2RGB)
    cv.imwrite('./output/largest.png', black)
    minvote = 0
    maxvote = 500
    houghImg = np.zeros((int(height * ratio), int(width * ratio)), "uint8")
    lines = cv.HoughLines(erode,1,np.pi/180,50)
    correctLines = list()
    thetaErr = math.pi / 6
    rhoErr = 180
    for line in lines:
        rho,theta = line[0]
        isNew = True
        for l in correctLines:
            if abs(theta - l[1]) < thetaErr and abs(rho - l[0]) < rhoErr:
                isNew = False
        if isNew:
            correctLines.append((rho, theta))
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 2000*(-b))
            y1 = int(y0 + 2000*(a))
            x2 = int(x0 - 2000*(-b))
            y2 = int(y0 - 2000*(a))
            cv.line(img,(x1,y1),(x2,y2),(0,0,255),2)
            cv.line(houghImg, (x1,y1), (x2, y2), (255,255,255), 1)
        else:
            continue
    #print(correctLines)
    contourImg, contours, hierarchy = cv.findContours(houghImg, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    error = 0.01
    quadri = list()
    for contour in contours:
        epsilon = error * cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, epsilon, True)
        if len(approx) == 4:
            quadri.append(approx)
    houghImg = cv.cvtColor(houghImg, cv.COLOR_GRAY2RGB)
    if len(quadri) == 0:
        print("Error, contours not found")
        cv.drawContours(houghImg, contours, -1, (255,255,0), 2)
        return originalImg
    else:
        maxcontour = max(quadri, key = getArea)
        cv.drawContours(houghImg, [maxcontour], -1, (0,255,0), 2)
        cv.imwrite('./output/hough.png', houghImg)
        contourPoints = np.array([x[0] for x in maxcontour], dtype = "float32")
        topLeft, topRight, bottomRight, bottomLeft = getOrderPoints(contourPoints)
        oldCorners = np.array([topLeft, topRight, bottomRight, bottomLeft], dtype = "float32")
        #Compute new width and height
        newWidth = max(getDistance(topLeft, topRight), getDistance(bottomLeft, bottomRight))
        newHeight = max(getDistance(topLeft, bottomLeft), getDistance(topRight, bottomRight))
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
