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

points = [po.pointMass(700, 100, 100, screen), po.pointMass(700, 100, 150, screen), po.pointMass(700, 20, 120, screen)]
#points = [po.pointMass(10, 400, 10, screen), po.pointMass(10, 400, 50, screen)]

poly1 = po.polygon(points, screen)
poly2 = po.polygon([poly1.points[1], poly1.points[2], po.pointMass(700, 110, 110, screen)], screen)
poly3 = po.polygon([poly1.points[0], poly2.points[2]], screen)
poly4 = po.regularPolygon((400,100), 6, 20, screen)

smpTest2 = po.springMassBody(poly1, screen, 0)
smpTest3 = po.springMassBody(poly2, screen, 0)
smpTest4 = po.springMassBody(poly3, screen, 0)
smpTest5 = po.springMassBody(poly4, screen, 0)

ground = po.collider(width, height, screen)

l = 0
lvect = []

#ENGINEMANAGER = em.engineManager([smpTest2, smpTest3, linkTest, linkTest2])
#ENGINEMANAGER = em.engineManager([smpTest2, smpTest3, smpTest4])
ENGINEMANAGER = em.engineManager([smpTest5])

def quitRoutine():
    #y = np.asarray(lvect)
    #x = np.arange(0, len(lvect))
    #plt.plot(x,y)
    #plt.show()
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
        smpTest5.points[1].isPinned = 1
        smpTest5.points[1].posX = pygame.mouse.get_pos()[0]
        smpTest5.points[1].posY = pygame.mouse.get_pos()[1]
        for point in smpTest5.points:
            point.totalYforce = 0
            point.totalXforce = 0
    else:
        smpTest5.points[1].isPinned = 0

    #l = po.vectorModulus(smpTest2.points[0].getPosition(),smpTest2.points[1].getPosition())

    #lvect.append(l)
    physic_init()
    ENGINEMANAGER.update()

    pygame.display.flip()
#fine mainloop