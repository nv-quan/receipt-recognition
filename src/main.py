import cv2 as cv
import numpy as np
import sys
import preprocess as pre

inp = sys.argv[1]
img = cv.imread(inp)
changeview = pre.changeView(img)
cv.imwrite('./output/changeview.png', changeview)
img = cv.imread('./output/changeview.png',0)
output = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,101,2)
            
canny = cv.Canny(img, 50,200)
#kernel = np.ones((3,3),np.uint8)
#canny = cv.morphologyEx(canny, cv.MORPH_CLOSE, kernel)
#output = cv.bitwise_not(canny)
cv.imwrite('./output/output.png', output)
