#Fixing bug in line 118. Bug in input 004
import cv2 as cv
from scipy import stats
import numpy as np
import math
from scipy import ndimage
debug = False
report = False
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
    if debug:
        print(line1)
        print(line2)
    rho1, theta1 = line1
    rho2, theta2 = line2
    A = np.array([[math.cos(theta1), math.sin(theta1)],
                [math.cos(theta2), math.sin(theta2)]])
    B = np.array([rho1, rho2]) 
    if debug:
        print(A)
        print(B)
    #return form: np.array([x, y]), may raise exception
    result = np.linalg.solve(A, B) 
    return result
def getBoundaryIntersections(line, img):
    rho = line[0]
    theta = line[1]
    if theta >= math.pi / 2:
        newTheta = theta - math.pi / 2
    else:
        newTheta = theta + math.pi / 2
    height = img.shape[0]
    width = img.shape[1]
    leftBound = (0, 0)
    rightBound = (width, 0)
    topBound = (0, math.pi / 2)
    bottomBound = (height, math.pi / 2)
    bounds = (leftBound, rightBound, topBound, bottomBound)
    intersections = list()
    for bound in bounds:
        try:
            intersection = getIntersection(line, bound)
        except np.linalg.linalg.LinAlgError:
            continue
        else:
            intersections.append(intersection)
    rhos = [getRho(newTheta)(point) for point in intersections]
    intersections = np.array(intersections)
    numPoints = len(intersections)
    if numPoints == 4:
        return list(intersections[np.argsort(rhos)][1:3])
    elif numPoints == 2:
        return list(intersections)
    else:
        raise Exception("Error in GetBoundaryIntersections: Not enough points")
#Geting `rho` of a line that goes through `point` with angle `theta`
def getRho(theta):
    def result(point):
        #point is of the form (x, y)
        return point[0] * math.cos(theta) + point[1] * math.sin(theta)
    return result
def checkSimilarRho(line, correctLine, img, rhoErr = 20):
    rho, theta = line
    intersections = getBoundaryIntersections(correctLine, img)
    rhos = [getRho(theta)(intersection) for intersection in intersections]
    if rho < max(rhos) + rhoErr and rho > min(rhos) - rhoErr:
        return True
    return False
def getParallel(line, point):
    rho, theta = line
    return getRho(theta)(point), theta
def changeView(originalImg):

    #------------Some constants----------------
    #Minimum angle different needed between 2 lines for them to be detect as separated
    thetaErr = math.pi / 6
    #Minimum space between 2 lines for them to be detected as separated
    rhoErr = 20 

    #------------Helper functions--------------
    def getLength(contour):
        return cv.arcLength(contour, False)
    def checkSimilarAngle(theta1, theta2):
        if theta1 <= thetaErr / 2 and theta2 >= math.pi - thetaErr / 2:
            return True#, (theta1, theta2)
        elif theta2 <= thetaErr / 2 and theta1 >= math.pi - thetaErr / 2:
            return True#, (theta2, theta1)
        elif abs(theta1 - theta2) < thetaErr:
            return True#, (theta1, theta2)
        else:
            return False#, None
    #get missing edges in case only three edges are detected
    #return [lonely edges, pair edges]
    def getMissingEdges(correctLines):
        if checkSimilarAngle(correctLines[0][1], correctLines[1][1]):
            return [correctLines[2], correctLines[0], correctLines[1]]
        elif checkSimilarAngle(correctLines[0][1], correctLines[2][1]):
            return [correctLines[1], correctLines[0], correctLines[2]]
        else:
            return correctLines
    #Draw lines into img, `diagonal` is the diagonal of img
    def drawLines(lines, img, diagonal, thick = 3):
        for line in lines:
            rho, theta = line
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + math.ceil(diagonal) * (-b))
            y1 = int(y0 + math.ceil(diagonal) * a)
            x2 = int(x0 - math.ceil(diagonal) * (-b))
            y2 = int(y0 - math.ceil(diagonal) * a)
            cv.line(img, (x1,y1), (x2, y2), (255,255,255), thick)
        if debug == True:
            print(lines)
    #resize image for faster processing
    def resizeImg(img):
        width = img.shape[1]
        height = img.shape[0]
        if width > 700:
            ratio = 500 / width
            resized = cv.resize(img, None, fx = ratio, fy = ratio, interpolation = cv.INTER_LINEAR) 
            newWidth = 500
            newHeight = int(height * ratio)
            return resized, ratio, newWidth, newHeight
        else:
            if width < 300:
                print("Warning: Image is too small")
            return img, 1, width, height
    #get 2 intersections of a line with boundaries of `img`
    height = originalImg.shape[0]
    width = originalImg.shape[1]
    diagonal = math.sqrt(height ** 2 + width ** 2)
    img, ratio, newWidth, newHeight = resizeImg(originalImg)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    if report:
        cv.imwrite('./report/gray.png', gray)
        ch = ['h', 's', 'v']
        for i in range(3):
            cv.imwrite('./report/' + ch[0] + '.png', hsv[:,:,i])
    ksize = (5,5)
    s = hsv[:,:,1]
    blurGray = cv.GaussianBlur(gray, ksize, 0)
    blurS = cv.GaussianBlur(s, ksize, 0)
    if report:
        cv.imwrite('./report/blur.png', blurGray)
        cv.imwrite('./report/blurS.png', blurS)
    threshold1 = 50
    threshold2 = 200
    edgesGray = cv.Canny(blurGray, threshold1, threshold2)
    edgesS = cv.Canny(blurS, threshold1, threshold2)
    if report:
        cv.imwrite('./report/edgesGray.png', edgesGray)
        cv.imwrite('./report/edgesS.png', edgesS)
    contourImgGray, contoursGray, hierarchyGray = cv.findContours(edgesGray, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contourImgS, contoursS, hierarchyS = cv.findContours(edgesS, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if report:
        allcontour = cv.cvtColor(edgesGray.copy(), cv.COLOR_GRAY2BGR)
        cv.drawContours(allcontour, contoursGray, -1, (0,255,0), 2)
        cv.imwrite('./report/contours.png', allcontour)
        #write report for S space
    maxcontourGray  = max(contoursGray, key = getLength)
    maxcontourS = max(contoursS, key = getLength)
    black = np.zeros((newHeight, newWidth), "uint8")
    cv.drawContours(black, [maxcontourGray], -1, (255,255,255), 1)
    cv.drawContours(black, [maxcontourS], -1, (255,255,255), 1)
    if report:
        cv.imwrite('./report/maxcontour.png', black)
    if debug:
        cv.imwrite('./output/largest.png', black)
    lines = cv.HoughLines(black,1,np.pi/180, 50)
    if report:
        blackHough = np.zeros((int(height * ratio), int(width * ratio)), "uint8")
        if len(lines) == 0:
            raise Exception('Error: There are no lines that have been detected')
        else:
            drawLines(lines[:,0,:], blackHough, diagonal, 1)
        cv.imwrite('./report/alllines.png', blackHough)
    correctLines = list()
    if debug:
        print("Diagonal %d" % diagonal)
    for line in lines:
        if len(correctLines) == 4:
            break
        rho,theta = line[0]
        isNew = True
        numSimilar = 0
        for l in correctLines:
            correctTheta = l[1]
            if checkSimilarAngle(theta, correctTheta):
                numSimilar += 1
                if numSimilar == 2:
                    isNew = False
                    break
                if checkSimilarRho(line[0], l, img, rhoErr):
                    isNew = False
                    break
        if isNew:
            correctLines.append([rho, theta])
        else:
            continue
    for line in correctLines:
        line[0] = line[0] / ratio
    numLines = len(correctLines)
    if numLines < 3:
        raise Exception("Error: Receipt does not have enough edges to detect!")
    elif numLines == 3:
        correctLines = getMissingEdges(correctLines)
        rho, theta = correctLines[0]
        intersections = getBoundaryIntersections(correctLines[1], originalImg) + getBoundaryIntersections(correctLines[2], originalImg)
        intersections.sort(key = getRho(theta))
        if abs(getRho(theta)(intersections[1]) - rho) > abs(getRho(theta)(intersections[2]) - rho):
            newLine = getParallel(correctLines[0], intersections[1])
        else:
            newLine = getParallel(correctLines[0], intersections[2])
        correctLines.append(newLine)
    corners = list()
    for i in range(4):
        for j in range(i + 1, 4):
            if checkSimilarAngle(correctLines[i][1], correctLines[j][1]):
                continue
            try:
                intersection = getIntersection(correctLines[i], correctLines[j])
            except np.linalg.linalg.LinAlgError:
                continue
            else:
                corners.append(intersection)
    if len(corners) != 4:
        raise Exception('Error: Cannot get correct corners')
    topLeft, topRight, bottomRight, bottomLeft = getOrderPoints(np.array(corners, dtype = "float32"))
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
    if report:
        cv.imwrite('./report/output.png', resultImage)
    return resultImage
#find a better way to binarize
def binarize(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #thresh = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    return img
