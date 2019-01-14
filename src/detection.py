import cv2 as cv
import numpy as np
import preprocess as pre
import matplotlib.pyplot as plt
import time

def findText(img):
    start = time.time()
    black = np.zeros((img.shape[0], img.shape[1]), "uint8")
    kernel = np.ones((1,15),np.uint8)
    dst = cv.cornerHarris(img,2,3,0.04)
    dst = cv.dilate(dst,kernel)
    black[dst>0.01*dst.max()]= 255
    closing = cv.morphologyEx(black, cv.MORPH_CLOSE, kernel)
    cv.imshow('Closing', closing)
    cv.waitKey(0)
    cv.destroyAllWindows()
    closing, contours, hierarchy = cv.findContours(closing, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    minwidth = 7
    for cnt in contours:
        x,y,w,h = cv.boundingRect(cnt)
        if h > minwidth:
            y -= 2
            h += 4
            cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
    end = time.time()
    print(end - start)
    cv.imwrite('./output/box.png', img)
