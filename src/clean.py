import cv2 as cv
import numpy as np
import preprocess as pre
import matplotlib.pyplot as plt
import time
import math
from scipy import stats
'''
def countNonZero(img):
    count = 0
    for px in img.ravel():
        if px != 0:
            count += 1
    return count
    '''
class ConnectedComponents:
    def __init__(self, img, contour):
        self.contour = contour
        self.rect = cv.boundingRect(contour)
        x,y,w,h = self.rect
        self.windowImg = img[y:y + h, x:x + w]
        self.rectArea = w * h
        self.whiteNum = cv.countNonZero(self.windowImg)
        self.whiteRatio = cv.countNonZero(self.windowImg) / self.rectArea
        if h / w > 1:
            HWRatio = w / h
            longer = h
        else:
            HWRatio = h / w
            longer = w
        self.HWRatio = HWRatio
        self.longer = longer
_WHITE = 0
def findContinuous(array):
    length = len(array)
    i = 0
    result = list()
    while i < length:
        if array[i] != _WHITE:
            start = i
            j = i + 1
            while j < length and array[j] != _WHITE:
                j += 1
            end = j
            result.append((start, end))
            i = j
        else:
            i += 1
    return result
def deleteLongLines(binaryImg, threshold):
    height, width = binaryImg.shape
    #vertical search
    for col in range(width):
        continuousElements = findContinuous(binaryImg[:,col])
        for element in continuousElements:
            start, end = element
            if end - start > threshold:
                binaryImg[start:end, col] = _WHITE
    #horizontal search
    for row in range(height):
        continuousElements = findContinuous(binaryImg[row,:])
        for element in continuousElements:
            start, end = element
            if end - start > threshold:
                binaryImg[row, start:end] = _WHITE

#=============helper functions==============
def getX(rect):
    return rect[0]
def getY(rect):
    return rect[1]
def getW(rect):
    return rect[2]
def getH(rect):
    return rect[3]

#=============main function=================
def findText(img, outputName = 'box.png', color = cv.IMREAD_GRAYSCALE):
    height = img.shape[0]
    width = img.shape[1]
    #change colorspace to gray in case color img is loaded
    if color != cv.IMREAD_GRAYSCALE:
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #get edges
    canny = cv.Canny(img, 100, 200)
    cv.imwrite('./output/canny' + outputName, canny)
    dilateKernel = np.ones((5,5), np.uint8)
    #get interest regions
    interest = cv.dilate(canny, dilateKernel)
    processImg = img.copy()
    processImg[interest == 0] = 255
    cv.imwrite('./output/interest' + outputName, processImg)

    #===========local thresholding===========
    #division constant
    hdiv = 20
    wdiv = 30
    boxHeight = int(height / hdiv)
    boxWidth = int(width / wdiv)
    x = 0
    #perform thresholding
    while x < width:
        xnew = min(x + boxWidth, width)
        y = 0
        while y < height:
            ynew = min(y + boxHeight, height)
            #dstTemp = dst[y:ynew,x:xnew]
            imgTemp = processImg[y:ynew,x:xnew]
            retval, threshTemp = cv.threshold(imgTemp[imgTemp < 255], 0, 255, cv.THRESH_OTSU)
            _,processImg[y:ynew,x:xnew] = cv.threshold(imgTemp, retval, 255, cv.THRESH_BINARY_INV)
            y = ynew
        x = xnew

'''
    #===============delete long lines================
    maxLengthCoef = 30
    #minimum length to be deleted
    threshold = height / maxLengthCoef
    deleteLongLines(processImg, threshold)
    cv.imwrite('./output/'+outputName, processImg)
    '''
    _,contours,hierarchy = cv.findContours(processImg, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    colorImg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    connectedComponents = list()
    for contour in contours:
        connectedComponents.append(ConnectedComponents(processImg, contour))
    WRLowThreshold = 1/3
    HWThreshold = 0.35
    longThreshold = 6
    for component in connectedComponents:
#        print(str(component.whiteNum) + '\t' + str(component.whiteRatio) + '\t' + str(component.HWRatio) + '\t' + str(component.longer))
        if component.whiteRatio > WRLowThreshold and component.HWRatio > HWThreshold and component.longer > longThreshold:
            x,y,w,h = component.rect
            cv.rectangle(colorImg, (x,y), (x+w,y+h), (0,0,255))
    cv.imwrite('./output/contour.png', colorImg)
