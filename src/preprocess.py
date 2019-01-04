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
def houghTransform(edges):
    maxval = 0
    imrows, imcols = edges.shape
    houghRows = math.ceil(math.sqrt(imrows ** 2 + imcols ** 2))
    houghCols = 200
    angles = np.zeros(houghCols)
    for col in range(houghCols):
        angles[col] = col * 2 *  math.pi / houghCols
    houghSpace = np.zeros((houghRows, houghCols), np.int_)
    for col in range(imcols):
        for row in range(imrows):
            if edges[row, col] != 0:
                x = col
                y = row
                for i in range(houghCols):
                    theta = angles[i]
                    rho = abs(x * math.cos(theta) + y * math.sin(theta))
                    houghSpace[int(rho), i] += 1
                    if maxval < houghSpace[int(rho), i]:
                        maxval = houghSpace[int(rho), i]
    return houghSpace, maxval
def getCorners(points):
    print(points)
    corners = np.zeros((4,2))
    for i in range(4):
        theta1 = points[i,1] / 200 * 2 * math.pi #fix 200
        theta2 = points[(i + 1) % 4, 1] / 200 * 2 * math.pi #fix 200
        rho1 = points[i,0]
        rho2 = points[(i + 1) % 4, 0]
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
    hough, maxval = houghTransform(edges)
    cv.imwrite('./output/hough.png', hough)
    kernel = (101,101)
    maxima = ndimage.maximum_filter(hough, kernel)
    minima = ndimage.minimum_filter(hough, kernel)
    linesidx = np.where((maxima == hough) & ~(minima == hough))
    #lines = np.where(maxima == hough)
    #linesidx = linesidx[np.array([0,1,2,3]), np.array([0,1,2,3])]
    print(linesidx)
    linesval = hough[linesidx]
    valarg = np.argpartition(linesval, 4)
    print(valarg)
    lines = np.array([(linesidx[1][i], linesidx[0][i])  for i in valarg])
    print(lines)
    hough = cv.imread('./output/hough.png')
    for i in range(4):
        line = lines[i]
        print(tuple(line))
        cv.circle(hough, tuple(line), 10, (0,255,0), 4)
    #getCorners(lines)
    #print(getCorners(lines))
    for i in range(len(lines)):
        cv.line(img, (0, int(lines[i,0] / math.cos(lines[i,1]))), (int(lines[i,0]/math.sin(lines[i,1])),0), (0,255,0), 5)
    cv.imwrite('./output/lines.png', img)    
    cv.imwrite('./output/maxima.png', maxima)
    cv.imwrite('./output/houghMarked.png', hough)
