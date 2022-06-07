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

points = [po.pointMass(10, 400, 10, screen), po.pointMass(10, 400, 50, screen), po.pointMass(10, 300, 50, screen)]
#points = [po.pointMass(10, 400, 10, screen), po.pointMass(10, 400, 50, screen)]

polyTest = po.polygon(points, screen)

smpTest2 = po.springMassBody(polyTest, screen, 1)

ground = po.collider(width, height, screen)

l = 0
lvect = []

def quitRoutine():
    y = np.asarray(lvect)
    x = np.arange(0, len(lvect))
    plt.plot(x,y)
    plt.show()
    print("fine simulazione")

def physic_init():
    for item in ENGINEMANAGER.objs:
        item.initialize()

render = 1

#ENGINEMANAGER = em.engineManager([smpTest2, smpTest3, linkTest, linkTest2])
ENGINEMANAGER = em.engineManager([smpTest2])

#mainloop
while render:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            quitRoutine()
            sys.exit()
            
    screen.fill((252,252,253))  

    if pygame.mouse.get_pressed()[0]:
        smpTest2.points[1].isPinned = 1
        smpTest2.points[1].posX = pygame.mouse.get_pos()[0]
        smpTest2.points[1].posY = pygame.mouse.get_pos()[1]
    else:
        smpTest2.points[1].isPinned = 0

    smpTest2.pinAPoint()

    l = po.vectorModulus(smpTest2.points[0].getPosition(),smpTest2.points[1].getPosition())

    lvect.append(l)
    physic_init()
    ENGINEMANAGER.update()

    pygame.display.flip()
#fine mainloop