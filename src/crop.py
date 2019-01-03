def getDistance(a,b):
    return np.linalg.norm(a - b)
    
def getOrderPoints(points):
    #divide points into 2 part: left and right
    #sort the points based on x-coordinates
    print(points)
    sortArgX = np.argsort(points[:,0]) 
    left = np.array([points[x] for x in sortArgX[0:2]])
    right = np.array([points[x] for x in sortArgX[2:4]])
    #point with bigger y is bottomLeft and vice versa
    bottomLeft = left[np.argmax(left[:,1])]
    topLeft = left[np.argmin(left[:,1])]
    #point that is farther from the topLeft is bottomRight
    if getDistance(topLeft, right[0]) > getDistance(topLeft, right[1]):
        bottomRight = right[0]
        topRight = right[1]
    else:
        bottomRight = right[1]
        topRight = right[0]
    return (topLeft, topRight, bottomRight, bottomLeft)

def changeView(img, error = 0.02, debug = None):
    #debug is an empty list that will contain edges and contours
    #error is the error in Polygon approximation
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (5,5), 0)
    edges = cv.Canny(blur, 50, 200)
    im2 , contours, hierarchy  = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    res = list()
    # minarea = img.shape[0] * img.shape[1] / 2
    for contour in contours:
        epsilon = error * cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, epsilon, True)
        if len(approx) == 4:
            res.append(approx)
    if len(res) > 0:
        result = max(res, key = cv.contourArea)
        cv.drawContours(contourImg, [result], -1, (0,255,0), 3) 
    else:
        print("Contours not found")
    #-------This part is only for debugging purpose--------
    contourImage = None
    if debug != None:
        debug.append(edges)
        contourImage = img.copy()
    contourPoints = np.array([x[0] for x in result], dtype = "float32");
    topLeft, topRight, bottomRight, bottomLeft = getOrderPoints(contourPoints)
    oldCorners = np.array([topLeft, topRight, bottomRight, bottomLeft], dtype = "float32")
    cv.imwrite('./output/contours.png', contourImg)
    #Compute new width and height
    newWidth = max(getDistance(topLeft, topRight), getDistance(bottomLeft, bottomRight))
    newHeight = max(getDistance(topLeft, bottomLeft), getDistance(topRight, bottomRight))
    #Compute 4 new corners
    newCorners = np.array([
        [0, 0],
        [newWidth - 1, 0],
        [newWidth - 1, newHeight -1],
        [0, newHeight -1]], dtype = "float32")
    #Compute transformation matrix
    transMat = cv.getPerspectiveTransform(oldCorners, newCorners)
    #Transform
    resultImage = cv.warpPerspective(img, transMat, (newWidth, newHeight))
    cv.imwrite('./output/output.png', resultImage)
