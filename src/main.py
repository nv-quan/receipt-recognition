import cv2 as cv
import numpy as np
import sys
import preprocess as pre
import detection as dtc

inp = sys.argv[1]
if len(sys.argv) > 2:
    out = sys.argv[2]
else:
    out = 'output'
img = cv.imread(inp)
changeview = pre.changeView(img)
output = pre.binarize(changeview)            
dtc.findText(output)
cv.imwrite('./output/' + out + '.png', output)
