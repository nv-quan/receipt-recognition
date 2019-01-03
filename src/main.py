import cv2 as cv
import numpy as np
import sys
import preprocess as pre

#resize the image for faster processing
inp = sys.argv[1]
img = cv.imread(inp)
processed = pre.changeView(img)
cv.imshow('Preprocessed', processed)
cv.waitKey(0)
cv.destroyAllWindows()
