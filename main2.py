from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import sys, pygame
import physicsObjects as po
import numpy as np
from matplotlib import backend_managers, pyplot as plt 
from pygame.locals import *
import engineManager as em

pygame.init()
pygame.display.set_caption("Marto's soft bodies v1.0")

size = width, height = (800, 800)

screen = pygame.display.set_mode(size)

p1 = po.pointMass(100, 100, 100, screen)
p2 = po.pointMass(100, 150, 100, screen)
p3 = po.pointMass(100, 150, 150, screen)
p4 = po.pointMass(100, 100, 150, screen)
p5 = po.pointMass(700, 125, 60, screen)

b1 = po.beamElement(p1, p2, screen)
b2 = po.beamElement(p2, p3, screen)
b3 = po.beamElement(p3, p4, screen)
b4 = po.beamElement(p4, p1, screen)
b5 = po.beamElement(p1, p3, screen)
b6 = po.beamElement(p1, p5, screen)
b7 = po.beamElement(p2, p5, screen)

points = [p1, p2, p3, p4, p5]
beams = [b1, b2, b3, b4, b5, b6, b7]

ret = po. reticulate(points, beams, screen)
smRet = po.springMassBodyReticulate(ret, screen, p1)

ground = po.collider(width, height, screen)

l = 0
lvect = []


ENGINEMANAGER = em.engineManager([smRet])

def quitRoutine():
    print("fine simulazione")

def physic_init():
    for item in ENGINEMANAGER.objs:
        item.initialize()

render = 1

#mainloop
while render:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            quitRoutine()
            sys.exit()
            
    screen.fill((252,252,253))  

    if pygame.mouse.get_pressed()[0]:
        smRet.points[4].isPinned = 1
        smRet.points[4].posX = pygame.mouse.get_pos()[0]
        smRet.points[4].posY = pygame.mouse.get_pos()[1]
        for point in smRet.points:
            point.totalYforce = 0
            point.totalXforce = 0
    else:
        smRet.points[4].isPinned = 0

    #l = po.vectorModulus(smpTest2.points[0].getPosition(),smpTest2.points[1].getPosition())

    #lvect.append(l)
    physic_init()
    ENGINEMANAGER.update()

    pygame.display.flip()
#fine mainloop