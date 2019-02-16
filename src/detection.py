import cv2 as cv
import numpy as np
import preprocess as pre
import matplotlib.pyplot as plt
import time
import json
report = False
def findText(img):
    black = np.zeros((img.shape[0], img.shape[1]), "uint8")
    kernel = np.ones((1,15),np.uint8)
    dst = cv.cornerHarris(img,2,3,0.04)
    dst = cv.dilate(dst,kernel)
    black[dst>0.01*dst.max()]= 255
    closing = cv.morphologyEx(black, cv.MORPH_CLOSE, kernel)
    closing, contours, hierarchy = cv.findContours(closing, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    minwidth = 7
    textBoxes = list()
    for cnt in contours:
        x,y,w,h = cv.boundingRect(cnt)
        if h > minwidth:
            y -= 3
            h += 6
            info = (x,y,w,h)
            textBoxes.append(info)
            cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
    if report:
        cv.imwrite('./output/box.png', img)
        boxesFile = open('./output/textboxes.json','w')
        boxesFile.write(json.dumps(textBoxes, indent = 4))
        boxesFile.close()
    return textBoxes
def getOverlapRatio(rectA, rectB):
    xA1,yA1,wA,hA = rectA
    xA2,yA2 = xA1 + wA, yA1 + hA
    xB1,yB1,wB,hB = rectB
    xB2,yB2 = xB1 + wB, yB1 + hB
    intersectArea = max(0, min(xA2, xB2) - max(xA1, xB1)) * max(0, min(yA2, yB2) - max(yA1, yB1))
    areaA = wA * hA
    areaB = wB * hB
    ratio = intersectArea / areaA
    return ratio
def locateBoxes(boxes, samples):
    location = dict()
    for boxId in samples:
        sample = samples[boxId]
        maxratio = 0
        mostCorrectBox = None
        for box in boxes:
            ratio = getOverlapRatio(sample, box)
            if ratio > maxratio:
                maxratio = ratio
                mostCorrectBox = box
        location[boxId] = mostCorrectBox
    return location
def getBoxes(img, samples):
    return locateBoxes(findText(img), samples)

