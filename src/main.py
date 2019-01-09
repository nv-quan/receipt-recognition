import cv2 as cv
import numpy as np
import sys
import preprocess as pre

inp = sys.argv[1]
out = sys.argv[2]
img = cv.imread(inp)
changeview = pre.changeView(img)
output = pre.binarize(changeview)            
cv.imwrite('./output/' + out + '.png', output)
