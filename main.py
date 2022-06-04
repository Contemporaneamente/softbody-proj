from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import sys, pygame
import physicsObjects as po
import numpy
from matplotlib import pyplot as plt 
from pygame.locals import *

pygame.init()

size = width, height = (400, 400)

screen = pygame.display.set_mode(size)

points = [po.pointMass(10, 20, 50, screen), po.pointMass(10, 80, 80, screen)]
point3 = po.pointMass(10, 100, 100, screen)

polyTest = po.polygon(points, screen)
rPolyTest = po.regularPolygon((200,200), 3, 50, screen)

smpTest1 = po.springMassBody(polyTest, screen, 1)
smpTest1.boundaryCond2P()

smpTest2 = po.springMassBody(rPolyTest, screen, 1)
smpTest2.boundaryCond()

linkPoly = po.polygon([point3, smpTest2.points[2]], screen)
linkTest = po.springMassBody(linkPoly, screen, 0)

ground = po.collider(width, height, screen)

def quitRoutine():
    print("fine simulazione")

render = 1

#mainloop
while render:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            quitRoutine()
            sys.exit()
            
    screen.fill((252,252,253))

    if event.type == MOUSEBUTTONDOWN:
            if event.button == 1: # 1 == left button
                smpTest2.points[1].posX = event.pos[0]
                smpTest2.points[1].posY = event.pos[1]

    smpTest2.initialize()
    linkTest.initialize()
    
    ground.draw()

    pygame.display.flip()
#fine mainloop