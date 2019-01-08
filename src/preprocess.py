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
def changeView(originalImg):
    def getLength(contour):
        return cv.arcLength(contour, False)
    height = originalImg.shape[0]
    width = originalImg.shape[1]
    img = originalImg
    ratio = 1
    if width > 700:
        ratio = 500 / width
        img = cv.resize(originalImg, None, fx = ratio, fy = ratio, interpolation = cv.INTER_LINEAR) 
    elif width < 300:
        print("Warning: Image is too small")
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
    cv.imwrite('./output/largest.png', black)
    kernel = (7,7)
    closing = cv.morphologyEx(black, cv.MORPH_CLOSE, kernel)
    contourImg, contours, hierarchy = cv.findContours(closing, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cv.imwrite('./output/closing.png', closing)
    cv.cvtColor(black, cv.COLOR_GRAY2BGR)
    houghImg = np.zeros((height, width), "uint8")
    lines = cv.HoughLines(closing,1,np.pi/180,50)
    correctLines = list()
    thetaErr = math.pi / 6
    rhoErr = 50
    diagonal = math.sqrt(height ** 2 + width ** 2)
    for line in lines:
        if len(correctLines) == 4:
            break
        rho,theta = line[0]
        isNew = True
        for l in correctLines:
            if theta <= thetaErr / 2 and l[1] >= math.pi - thetaErr / 2:
                if abs(rho + l[0]) < rhoErr and abs(theta + math.pi - l[1]) < thetaErr:
                    isNew = False
            elif l[1] <= thetaErr / 2 and theta >= math.pi - thetaErr / 2:
                if abs(rho + l[0]) < rhoErr and abs(l[1] + math.pi - theta) < thetaErr:
                    isNew = False
            else:
                if abs(theta - l[1]) < thetaErr and abs(rho - l[0]) < rhoErr:
                    isNew = False
        if isNew:
            correctLines.append((rho, theta))
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho / ratio
            y0 = b*rho / ratio
            x1 = int(x0 + math.ceil(diagonal) * (-b))
            y1 = int(y0 + math.ceil(diagonal) * a)
            x2 = int(x0 - math.ceil(diagonal) * (-b))
            y2 = int(y0 - math.ceil(diagonal) * a)
            cv.line(houghImg, (x1,y1), (x2, y2), (255,255,255), 1)
        else:
            continue
    print(correctLines)
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
        cv.imwrite('./output/hough.png', houghImg)
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
        resultImage = cv.warpPerspective(originalImg, transMat, (newWidth, newHeight))
        return resultImage
def binarize(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    thresh = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    kernel = np.ones((5,5),np.uint8)
    closing = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel)
    return closing
