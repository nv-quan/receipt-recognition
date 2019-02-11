import cv2 as cv
import numpy as np
import sys
import preprocess as pre
import detection as dt
import json

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
#    print(json.dumps(detected, indent = 4))
    for boxId in detected:
        if detected[boxId] == None:
            continue
        x,y,w,h = detected[boxId]
        cv.rectangle(stdSizeImg, (x,y), (x + w, y + h), (0, 255, 0), 2)
        cv.putText(stdSizeImg, boxId, (x,y), cv.FONT_HERSHEY_PLAIN, 1.0, (255,255,0), 2)
    cv.imshow('test', stdSizeImg)
    cv.waitKey(0)
    cv.destroyAllWindows()

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
