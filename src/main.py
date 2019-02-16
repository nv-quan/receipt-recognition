import cv2 as cv
import numpy as np
import sys
import preprocess as pre
import detection as dt
import json
import clean
import pytesseract

#Main function
def main():
    sample = json.load(sampleFile)
    img = cv.imread(inp)
    pre.debug = debugFlag
    pre.report = reportFlag
    changeview = pre.changeView(img)
    if reportFlag:
        cv.imwrite('./output/changeview.png', changeview)
    stdH = sample['document']['height']
    stdW = sample['document']['width']
    stdSizeImg = cv.resize(changeview, (stdW, stdH))
    gray = cv.cvtColor(stdSizeImg, cv.COLOR_BGR2GRAY)
    dt.report = reportFlag
    detected = dt.getBoxes(gray, sample['boxes'])
    tesseractConfig = ("-l eng --oem 3 --psm 7")
#    print(json.dumps(detected, indent = 4))
    ocr = dict()
    for boxId in detected:
        if detected[boxId] == None:
            continue
        x,y,w,h = detected[boxId]
        cv.rectangle(stdSizeImg, (x,y), (x + w, y + h), (0, 255, 0), 2)
        cv.putText(stdSizeImg, boxId, (x,y), cv.FONT_HERSHEY_PLAIN, 1.5, (255,255,0), 1)
        roi = stdSizeImg[y:y + h,x: x + w]
        text = pytesseract.image_to_string(roi, config=tesseractConfig)
        ocr[boxId] = text 
    cv.imshow('test', stdSizeImg)
    cv.waitKey(0)
    cv.destroyAllWindows()
    print(json.dumps(ocr, indent = 4))
    clean.findText(changeview, color = cv.IMREAD_COLOR)
    

#Global constant (do not change)
debugFlag = False
reportFlag = False
inp = None
sampleFile = None

#Load and run configuration
configFile = open('./src/config.json','r')
config = json.load(configFile)
sampleFile = open(config['sample'], 'r')
#run mode
if 'debug' in config['run mode']:
    debugFlag = True
if 'report' in config['run mode']:
    reportFlag = True
#input mode
if config['input mode'] == 'single':
    inp = config['input file']
    main()
elif config['input mode'] == 'folder':
    pass
#output
if config['output name'] == 'input':
    pass
configFile.close()
sampleFile.close()
