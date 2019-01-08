import cv2 as cv
from scipy import stats
import numpy as np
import math
from scipy import ndimage
debug = True
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
def getIntersection(line1, line2):
    #lines are of the form (rho, theta)
    print(line1)
    print(line2)
    rho1, theta1 = line1
    rho2, theta2 = line2
    A = np.array([[math.cos(theta1), math.sin(theta1)],
                [math.cos(theta2), math.sin(theta2)]])
    B = np.array([rho1, rho2]) 
    print(A)
    print(B)

    #return form: np.array([x, y])
    try:
        result = np.linalg.solve(A, B) 
    except np.linalg.linalg.LinAlgError:
        return (math.inf, math.inf)
    else:
        return result
def changeView(originalImg):
    def getLength(contour):
        return cv.arcLength(contour, False)
    def checkSimilarAngle(theta1, theta2):
        if theta1 <= thetaErr / 2 and theta2 >= math.pi - thetaErr / 2:
            return True, (theta1, theta2)
        elif theta2 <= thetaErr / 2 and theta1 >= math.pi - thetaErr / 2:
            return True, (theta2, theta1)
        else:
            return False, None
    #get missing edges in case only three edges are detected
    #return [lonely edges, pair edges]
    def getMissingEdges(correctLines):
        if checkSimilarAngle(correctLines[0][1], correctLines[1][1]):
            return [correctLines[2], correctLines[0], correctLines[1]]
        elif checkSimilarAngle(correctLines[0][1], correctLines[2][1]):
            return [correctLines[1], correctLines[0], correctLines[2]]
        else:
            return correctLines
    def getRho(theta):
        def result(point):
            #point is of the form (x, y)
            return point[0] * math.cos(theta) + point[1] * math.sin(theta)
        return result
    height = originalImg.shape[0]
    width = originalImg.shape[1]
    img = originalImg
    ratio = 1
    #resize image for faster processing
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
    if debug == True:
        cv.imwrite('./output/largest.png', black)
    kernel = (7,7)
    closing = cv.morphologyEx(black, cv.MORPH_CLOSE, kernel)
    contourImg, contours, hierarchy = cv.findContours(closing, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cv.cvtColor(black, cv.COLOR_GRAY2BGR)
    houghImg = np.zeros((height, width), "uint8")
    lines = cv.HoughLines(closing,1,np.pi/180,50)
    correctLines = list()
    thetaErr = math.pi / 4
    rhoErr = 20 #need to change this mechanism to work with 021.png
    diagonal = math.sqrt(height ** 2 + width ** 2)
    for line in lines:
        if len(correctLines) == 4:
            break
        rho,theta = line[0]
        isNew = True
        for l in correctLines:
            check = checkSimilarAngle(theta, l[1])
            if check[0]:
                theta1, theta2 = check[1]
                if abs(rho + l[0]) < rhoErr + diagonal * math.sin(abs(theta1 + math.pi - theta2)) and abs(theta1 + math.pi - theta2) < thetaErr:
                    isNew = False
            elif abs(theta - l[1]) < thetaErr and abs(rho - l[0]) < rhoErr + math.sin(abs(theta - l[1])) * diagonal:
                isNew = False
        if isNew:
            correctLines.append([rho, theta])
        else:
            continue
    for line in correctLines:
        line[0] = line[0] / ratio
    numLines = len(correctLines)
    if numLines < 3:
        print("Error: Receipt does not have enough edges to detect!")
    elif numLines == 3:
        correctLines = getMissingEdges(correctLines)
        mainRho = correctLines[0][0]
        mainTheta = correctLines[0][1]
        leftBound = (0, 0)
        rightBound = (width, 0)
        topBound = (0, math.pi / 2)
        bottomBound = (height, math.pi / 2)
        bounds = (leftBound, rightBound, topBound, bottomBound)
        intersections = list()
        print(correctLines)
        print(bounds)
        for bound in bounds:
            for i in range(1,3):
                intersections.append(getIntersection(correctLines[i], bound))
        try:
            intersections.remove(math.inf)
        except ValueError:
            pass
        if debug:
            cv.imwrite('./output/original.png', originalImg)
            #for point in intersections:
                #cv.circle(originalImg, (int(point[1]), int(point[0])), 3, (0,255,0), 3)
        keysort = getRho(mainTheta)
        intersections.sort(key = keysort)
        print(intersections)
        rho1 = keysort(intersections[int(len(intersections) / 2) - 1])
        rho2 = keysort(intersections[int(len(intersections) / 2)])
        print(rho1)
        print(rho2)
        if abs(mainRho - rho1) > abs(mainRho - rho2):
            correctLines.append((rho1, mainTheta))
        else:
            correctLines.append((rho2, mainTheta))
    for line in correctLines:
        rho, theta = line
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + math.ceil(diagonal) * (-b))
        y1 = int(y0 + math.ceil(diagonal) * a)
        x2 = int(x0 - math.ceil(diagonal) * (-b))
        y2 = int(y0 - math.ceil(diagonal) * a)
        cv.line(houghImg, (x1,y1), (x2, y2), (255,255,255), 3)
    if debug == True:
        print(correctLines)
    kernel = (7,7)
    closing = cv.morphologyEx(houghImg, cv.MORPH_CLOSE, kernel)
    if debug == True:
        cv.imwrite('./output/closing.png', closing)
    contourImg, contours, hierarchy = cv.findContours(closing, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
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
        if debug == True:
            cv.imwrite('./output/hough.png', houghImg)
        return originalImg
    else:
        maxcontour = max(quadri, key = getArea)
        cv.drawContours(houghImg, [maxcontour], -1, (0,255,0), 2)
        contourImg = originalImg.copy() 
        cv.drawContours(contourImg, [maxcontour], -1, (0,255,0), 2)
        if debug == True:
            cv.imwrite('./output/hough.png', houghImg)
            cv.imwrite('./output/bound.png', contourImg)
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
        if debug == True:
            cv.imwrite('./output/changeview.png', resultImage)
        return resultImage
def binarize(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #thresh = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    return img
