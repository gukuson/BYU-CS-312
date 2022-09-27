from turtle import right
from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

class Node:
    def __init__(self, data = None):
        self.data = data
        self.next = self
        self.prev = self

class Hull:
    def __init__(self, point):
        self.left = Node(point)
        self.right = Node(point)
        
# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#

class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)
        

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        
        # SORT THE POINTS BY INCREASING X-VALUE
        def getX(point):
            return point.x()
        
        points = sorted(points, key = getX)

        t2 = time.time()
        
        hull = findConvexHull(points)
        
        polygon = createPolygon(hull)
        print(len(polygon))
        
        t3 = time.time()
        
        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText(
            'Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t1))
   
def createPolygon(hull):
    head = hull.left
    temp = hull.left
    polygon = []
    while True:
        polygon.append(QLineF(temp.data, temp.next.data))
        if (temp.next == head):
            break
        temp = temp.next
    return polygon

# If first parameter slope is more negative than 2nd parameter slope
def isMoreNegative(line1, line2):
    return (slope(line1) < slope(line2))

# If first parameter slope is more positive than 2nd parameter slope
def isMorePositive(line1, line2):
    return (slope(line1) > slope(line2))
        
def slope(line):
    return ((line.y2() - line.y1()) / (line.x2() - line.x1()))
        
def findUpperTangent(leftHull, rightHull):
    rightOfLeft = leftHull.right
    leftOfRight = rightHull.left
    currLine = QLineF(rightOfLeft.data, leftOfRight.data)
    # currSlope = slope(currLine)
    notDone = True
    while notDone:
        notDone = False
        while isMoreNegative(QLineF(rightOfLeft.prev.data, leftOfRight.data), currLine):
            rightOfLeft = rightOfLeft.prev
            currLine = QLineF(rightOfLeft.data, leftOfRight.data)
            notDone = True
        while isMorePositive(QLineF(rightOfLeft.data, leftOfRight.next.data), currLine):
            leftOfRight = leftOfRight.next
            currLine = QLineF(rightOfLeft.data, leftOfRight.data)
            notDone = True
    return [rightOfLeft, leftOfRight]

def findLowerTangent(leftHull, rightHull):
    rightOfLeft = leftHull.right
    leftOfRight = rightHull.left
    currLine = QLineF(rightOfLeft.data, leftOfRight.data)
    notDone = True
    while notDone:
        notDone = False
        while isMorePositive(QLineF(rightOfLeft.next.data, leftOfRight.data), currLine):
            rightOfLeft = rightOfLeft.next
            currLine = QLineF(rightOfLeft.data, leftOfRight.data)
            notDone = True
        while isMoreNegative(QLineF(rightOfLeft.data, leftOfRight.prev.data), currLine):
            leftOfRight = leftOfRight.prev
            currLine = QLineF(rightOfLeft.data, leftOfRight.data)
            notDone = True
    return [rightOfLeft, leftOfRight]

def getLeftRightNodes(currNode):
    head = currNode
    left = currNode
    right = currNode
    while True:
        currNode = currNode.next
        if (currNode == head):
            break
        # If next node is more left then the farthest left point it becomes the new far left node
        if (currNode.data.x() < left.data.x()):
            left = currNode
        elif (currNode.data.x() > right.data.x()):
            right = currNode
    
    return (left, right)
    
        
def mergeHulls(leftHull, rightHull):
    upperNodes = findUpperTangent(leftHull, rightHull)
    lowerNodes = findLowerTangent(leftHull, rightHull)
    # Merging the upper tangent nodes to each other
    upperNodes[0].next = upperNodes[1]
    upperNodes[1].prev = upperNodes[0]
    
    # Merging the lower tangent nodes to each other
    lowerNodes[0].prev = lowerNodes[1]
    lowerNodes[1].next = lowerNodes[0]
    
    # Calculate farthest left and right node from new hull, starting at arbitrary point in hull
    (minX, maxX) = getLeftRightNodes(upperNodes[0])
    
    # Setting farthest left and right point in updated hull, arbitrarily chose leftHull to update to become new hull
    leftHull.left = minX
    leftHull.right = maxX
    
    return leftHull

def findConvexHull(points):
    if len(points) == 1:
        return Hull(points[0])
    half = len(points)//2
    left = points[:half]
    right = points[half:]
    
    return mergeHulls(findConvexHull(left), findConvexHull(right))
    
    