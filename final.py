from SimpleCV import *
import matplotlib.pyplot as plt
import numpy as np
import sys
import nxt, thread, time
from time import sleep
####################### IMAGE HANDLING FUNCTIONS ######################


#return the blob with the largest area in the given image
#I believe a blob is a connected region of one color.
def getBiggestBlob(img):
  blobs = img.findBlobs()
  if(blobs == None):
    return None
  maxBlob = blobs[0]
  maxArea = maxBlob.area()
  for i in range(1,len(blobs)):
    area = blobs[i].area()
    if(area>maxArea):
      maxArea = area
      maxBlob = blobs[i]
  return maxBlob
    

#returns the coordinates of the largest image of the given color as an array

def findObj(img,color):
  #convert image to grayScale, 
  #with each pixels value =  RED - the original value
  #then invert so we are looking for the highest valued pixel group
  cimg = img.colorDistance(color)
  cimg = cimg.invert()
  maxVal = cimg.getGrayNumpyCv2().max();
  cimg = cimg.threshold(maxVal-33);  #threshold to eliminate noise
  blob = getBiggestBlob(cimg)
  if(blob == None):
    return None
  return blob.coordinates()  #return the center of the object in the image

#returns the distance in pixels of two points in the image
def distance(pointA,pointB):
  x = abs(pointA[0]- pointB[0])
  y = abs(pointA[1]- pointB[1])
  return  np.sqrt( x*x + y*y)

#draws a filled, black circle in the image at the specified position
def drawCircle(img,coord):
  img.drawCircle((coord[0],coord[1]),5,Color.BLACK,-1)


def getBlobs(img,color):
  imgc = img.colorDistance(color).invert()
  a = imgc.getGrayNumpyCv2()
  imgc = imgc.threshold(a.max() - 80)
  return imgc.findBlobs()


def getCheckPointBlobs(img,color):
  imgc = img.colorDistance(color).invert()
  a = imgc.getGrayNumpyCv2()
  imgc = imgc.erode()  #get rid of noise from other lights
  imgc = imgc.dilate(5) #grow regions we want so they dont get thresholded
  imgc = imgc.threshold(a.max()-50)
  #imgc = imgc.dilate(3)  #smooth things a bit
  return imgc.findBlobs()  


def getCheckPointCoords(img,color):
  blobs = getCheckPointBlobs(img,color)
  coords = []
  for b in blobs:
    coords.append(b.coordinates())
  return coords


def getRobot(img,color):
  imgc = img.colorDistance(color).invert()
  a = imgc.getGrayNumpyCv2()
  imgc = imgc.threshold(a.max()-50) #get rid of everything but the color
  imgc = imgc.dilate(10)  #make the blobs by the lights bigger
  return getBiggestBlob(imgc)





## #########   ROBOT CONTROL     ################

#tells the motors to turn a certain amount with a given power
#  degrees - the amount of degrees the wheel turns
#  left/right Power  - the power of the left/right motors
def makeTurn(degrees,leftPower,rightPower):
  distance = degrees
  mx.run(rightPower) #turns on motor with given power indefinitely
  my.run(leftPower)
    #now see har far the motos have turned
  mx_target = mx.get_tacho().get_target(distance,-1)
  my_target = my.get_tacho().get_target(distance,-1)
  i = 0
  #while they haven't turned far enough, just spin(do nothing, i=0)
  while not mx.get_tacho().is_greater(mx_target,-1) and not my.get_tacho    ().is_greater(my_target,-1 ):
    i = 0

  mx.run(0)   #now we are out of the while loop, so turn the motors off
  my.run(0) 
  return None



##here we connect to the brick and get handles to the motors
b = nxt.find_one_brick()
mx = nxt.Motor(b, nxt.PORT_A)
my = nxt.Motor(b, nxt.PORT_B)
motors = [mx, my]
running = [False,False]
  
#here we connect to the camera through SimpleCV
cam = Camera()



#some definitions
STRAIGHT = 0
LEFT = 1
RIGHT = 2
distThresh = 80
DEBUG_VISUAL = True  #for visual debugging
DEBUG_PRINT = True  #for printing to the console debugging

objRadius = 2 #inches
robotRadius = 8 #inches
comboRadius = objRadius + robotRadius

dist = 100000
prevDist = dist +100






img = cam.getImage()  #get image from camera
robot = getRobot(img,Color.WHITE)
rCoord = robot.coordinates()
#checkPoints = getCheckPoints(img,Color.WHITE)
checkCoords = getCheckPointCoords(img,Color.RED) 
numCheckPoints = len(checkCoords)
dists = [] 
for i in range(0,numCheckPoints):
 # dists.append(distance(centers[i],robot))
  if(DEBUG_VISUAL):
    print('c')
    drawCircle(img,checkCoords[i])

if(DEBUG_VISUAL):
  img.drawCircle((rCoord[0],rCoord[1]),8,Color.GREEN,-1)
  img.show()












#### MAIN LOOP  - get camera data, and tell robot what to do accordingly
while(True):  
  #img = cam.getImage()  #get image from camera
  #robot = getRobot(img,Color.RED)
  #rCoord = robot.coordinates()
  ##checkPoints = getCheckPoints(img,Color.WHITE)
  #checkCoords = getCheckPointCoords(img,Color.WHITE) 
  #numCheckPoints = len(checkCoords)
  #dists = [] 
  #for i in range(0,numCheckPoints):
   ## dists.append(distance(centers[i],robot))
    #if(DEBUG_VISUAL):
     # drawCircle(img,checkCoords[i])

 # if(DEBUG_VISUAL):
  #  img.drawCircle((rCoord[0],rCoord[1]),8,Color.GREEN,-1)
   # img.show()

  go = True
  for point in checkCoords:
    while(go):
      img = cam.getImage()  #get image from camera
      robot = getRobot(img,Color.WHITE)
      rCoord = robot.coordinates()
      dist = distance(point,rCoord)

      if(DEBUG_VISUAL):
        img.drawCircle((rCoord[0],rCoord[1]),8,Color.GREEN,-1)
        drawCircle(img,point)
        img.show()


      if(dist>=distThresh):         #if we are not there yet, go
        go = True
        motors[0].run(-70)
        motors[1].run(-70)
      if(dist<distThresh):   #if we are there, stop
        go = False
        motors[0].run(0)
        motors[1].run(0)
        sleep(1)
        print('AWAKE')
        motors[0].run(70)
        motors[1].run(70)
        sleep(1)
        motors[0].run(0)
        motors[1].run(70)
        sleep(.5)
        motors[0].run(0)
        motors[1].run(0)
        #makeTurn(360,70,70)
        #print('AWAKE2')
        #makeTurn(360,80,0)
        #print('AWAKE3')
        #motors[0].brake()
        #motors[1].brake()
        #continue; #dont turn because we are already there




    #if we are getting further away. turn a little
      if((dist > prevDist)  and go):
        makeTurn(180,-80,0) #right turn
      prevDist = dist





