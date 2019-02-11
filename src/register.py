#document properties
#Type of size: Fixed or Variable
#Size: 
#width range from ... to ...
#height range from ... to ...
#Boxes properites
#Id
#x, y, w, h
#type of size: 
    #Fixed size
    #Variable size
#type of position:
    #Fixed position
    #Variable position
#N# of lines:
    #Fixed line (1,2,...)
    #Variable lines
#Range of properties:
    #x: From ... to ...
    #y: ... 
    #w
    #h
    #Number of lines: From ... to ...
#relative prosition
    #under list of boxes {id1, id2,... }
    #above list of boxes {id3, id4,... }
    #to the left of { }
    #to the right of { }
    #To be more specific
#Formula of confirmation

import cv2 
import numpy as np
import sys
import json

'''
docSizeType = input("Please input type of document (1: Fixed size, 2: Variable size) ") 
#Variable size is not working yet
docWidth = input("Please enter document width ")
docHeight = input("Please enter document height ")
docSample = input("Please enter sample image ")
'''
register = dict()
docWidth = 1000
docHeight = 666
docSample = './docsample/sam1.png'
image = cv2.imread(docSample)
docWidth = image.shape[1]
docHeight = image.shape[0]
docProperty = {
        "type" : "fix",
        "width" : int(docWidth),
        "height" : int(docHeight),
        "sample" : docSample
        }
register["document"]= docProperty
boxes = dict()
i = 0
while True:
    i += 1
    key = input("Press enter to continue, 'q' to quit: ")
    if key == 'q':
        break
    while True:
        boxId = input("Enter box id (leave blank for default): ")
        if boxId == '':
            boxId = i
        if not boxId in boxes:
            break
        else:
            print("This id already exists in the database.")
    wName = "Select box " + str(boxId)
    cv2.imshow(wName, image)
    r = cv2.selectROI(wName, image, False, False)
    cv2.destroyWindow(wName)
    boxes[boxId] = r
register["boxes"] = boxes
output = open('./docsample/sample.json', 'w')
output.write(json.dumps(register, indent = 4))
output.close()
