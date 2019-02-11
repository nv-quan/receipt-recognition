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
    stdH = config['document']['height']
    stdW = config['document']['width']
    stdSizeImg = cv.resize(changeview, (stdW, stdH))
    gray = cv.cvtColor(stdSizeImg, cv.COLOR_BGR2GRAY)
    dt.report = reportFlag
    textBoxes = dt.findText(gray)

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
if config['output name'] = 'input':
    pass
configFile.close()
sampleFile.close()
