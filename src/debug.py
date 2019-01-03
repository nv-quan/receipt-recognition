import cv2 as cv
import numpy as np
import sys
import preprocess as pre

inp = sys.argv[1]
img = cv.imread(inp)
debug = list()
processed = pre.changeView(img, 0.01, debug)
cv.imshow('Preprocessed', processed)
cv.waitKey(0)
cv.destroyAllWindows()
cv.imwrite('./output/edges.png', debug[0])
cv.imwrite('./output/contours.png', debug[1])
cv.imwrite('./output/detected.png', debug[2])
