import sys, pygame
import physicsObjects as po
pygame.init()

size = width, height = (400, 400)

screen = pygame.display.set_mode(size)

point1 = po.pointMass(10, 200, 200, screen) 
point2 = po.pointMass(10, 300, 300, screen) 
point3 = po.pointMass(10, 200, 300, screen) 

polyTest = po.polygon([point1, point2, point3], screen)

rbTest = po.rigidBody(po.polygon([point1, point2], screen))

smTest = po.springMassBody(point1, point2, screen)

render = 1

#mainloop
while render:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    
    screen.fill((252,252,253))

    polyTest.draw()

    pygame.draw.rect(screen, (50,50,50), (0, height - 30, width, 30))
    pygame.display.flip()
#fine mainloop




