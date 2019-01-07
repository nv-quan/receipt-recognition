import cv2 as cv
import numpy as np
import sys
import preprocess as pre

inp = sys.argv[1]
img = cv.imread(inp)
processed = pre.changeView(img)
cv.imwrite('./output/output.png', processed)
