import cv2 as cv
import numpy as np

def findText(img):
    '''
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    '''
    threshold1 = 50
    threshold2 = 200
    canny = cv.Canny(img, threshold1, threshold2)
    kernel = np.ones((5,5),np.uint8)
    dilation = cv.dilate(canny,kernel,iterations = 1)
    closing = cv.morphologyEx(dilation, cv.MORPH_CLOSE, kernel)
    img, contours, hierarchy = cv.findContours(closing, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cv.imshow('Test', closing)
    cv.waitKey(0)
    cv.destroyAllWindows()

