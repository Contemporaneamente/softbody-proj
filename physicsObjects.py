import math
import pygame
import itertools
import engineManager as em
import numpy as np

#------costanti------#
GRAVITY = 0.001
DAMPING = 1.47
STIFFNESS = 1.5
#------costanti------#

#------classi------#

#layer di collisione
class collisonLayer():
    def __init__(self):
        self.isGrounded = 0

#collisore work in progress
class collider:
    def __init__(self, posx, posy, surf: pygame.surface):
        self.posx = posx
        self.posy = posy
        self.boundary = posy
        self.surf = surf
    def draw(self):
        pygame.draw.rect(self.surf, (50,50,50), (0, self.posy - 30, self.posx, 30))

#massa puntiforme
class pointMass(collisonLayer, em.rObject):
    def __init__(self, mass, posX, posY, surf: pygame.surface):
        self.mass = mass
        self.posX = posX
        self.posY = posY
        self.radius = 5
        self.color = [255,10,10]
        self.surf = surf
        self.totalXforce = 0
        self.totalYforce = 0
        self.vx = 0
        self.vy = 0
        self.damping = 0.04
        self.isPinned = 0
    def draw(self):
        pygame.draw.circle(self.surf, self.color, [self.posX, self.posY], self.radius)
    def getPosition(self):
        return (self.posX, self.posY)

    def checkGroundCollision(self, collider: collider):
        if self.posY >= collider.boundary:
            self.isGrounded = 1

#elemento di connessione tra due punti
class beamElement(em.rObject):
    def __init__(self, pt1: pointMass, pt2: pointMass, surf: pygame.surface):
        self.pt1 = pt1
        self.pt2 = pt2
        self.pt1pos = pt1.getPosition()
        self.pt2pos = pt2.getPosition()
        self.color = [0,10,10]
        self.surf = surf
        self.stiffness = STIFFNESS
        self.damping = DAMPING
        self.l0 = vectorModulus(self.pt1pos, self.pt2pos)

    def getCurrentLenght(self):
        curLen = vectorModulus(self.pt1.getPosition(), self.pt2.getPosition()) 
        return curLen

    def getCurrentOrientation(self):
        curOr = beamDirection(self.pt1.getPosition(), self.pt2.getPosition())
        return curOr
    
    def getElasticForce(self):
        deltaL = self.getCurrentLenght() - self.l0 
        eForce = abs(deltaL) * self.stiffness 
        
        if self.getCurrentLenght() - self.l0 > 0:
            return -eForce
        else:
            return eForce

    def getDampingForce(self):
        normPos = np.linalg.norm([self.pt2.getPosition()[0]-self.pt1.getPosition()[0], self.pt2.getPosition()[1]-self.pt1.getPosition()[1]])
        normalizedPosVect = [(self.pt2.getPosition()[0]-self.pt1.getPosition()[0])/normPos, (self.pt2.getPosition()[1]-self.pt1.getPosition()[1])/normPos]
        relativeDot = np.dot(normalizedPosVect, [self.pt2.vx - self.pt1.vx, self.pt2.vy - self.pt1.vy])
        dForce = self.damping * componentModulus(self.pt2.vx - self.pt1.vx, self.pt2.vy - self.pt1.vy)
        if relativeDot > 0:
            return -dForce
        else:
            return dForce

    def draw(self):
        pygame.draw.line(self.surf, self.color, (self.pt1.posX, self.pt1.posY), (self.pt2.posX, self.pt2.posY), 2)

#poligono generico
class polygon(em.rObject):
    def __init__(self, points: list[pointMass], surf: pygame.surface):
        self.points = points
        self.beams = makeBeamsCombs(points, surf)
        self.contour = makeBeamsList(points, surf)
        self.surf = surf

    def draw(self):
        for beam in self.beams:
            beam.draw()
        for point in self.points:
            point.draw()
    
    def drawContour(self):
        for cont in self.contour:
            cont.draw()
        for point in self.points:
            point.draw()
    
    def getPoints(self):
        return self.points
        
    def getBeams(self):
        return self.beams

#poligono regolare 
class regularPolygon(polygon):
    def __init__(self, center: tuple, sidesNum, radius, surf: pygame.surface):
        self.center = center
        self.sidesNum = sidesNum
        self.radius = radius
        self.points = vertsToPoints(regularVertCalc(sidesNum, radius), surf)
        self.beams = makeBeamsCombs(self.points, surf)
        self.contour = makeBeamsList(self.points, surf)
        self.surf = surf

#------forme dotate di proprietà fisiche------#

#corpo rigido
class rigidBody(em.rObject):
    def __init__(self, polygon: polygon):
        self.polygon = polygon

    def draw(self):
        self.polygon.draw()

    def rigidTranslate(self, vector: tuple):
        points = self.polygon.getPoints()
        for point in points:
            point.posX += vector[0]
            point.posY += vector[1]

#oggetto spring-mass body completo 
class springMassBody(em.rObject):
    def __init__(self, poly: polygon, surf: pygame.surface, pinpoint):
        self.poly = poly
        self.points = poly.getPoints()
        self.beams = poly.getBeams()
        self.surf = surf
        self.gravity = 1
        self.pinpoint = pinpoint

    def computeElasticForcesOnPoint(self):
        for beam in self.beams:
            beam.pt1.totalXforce -= beam.getElasticForce() * math.cos(beam.getCurrentOrientation()) 
            beam.pt1.totalYforce -= beam.getElasticForce() * math.sin(beam.getCurrentOrientation())
            beam.pt2.totalXforce += beam.getElasticForce() * math.cos(beam.getCurrentOrientation()) 
            beam.pt2.totalYforce += beam.getElasticForce() * math.sin(beam.getCurrentOrientation()) 
    def computeDampingForcesOnPoint(self):
        for beam in self.beams:
            beam.pt1.totalXforce -= beam.getDampingForce() * math.cos(beam.getCurrentOrientation())
            beam.pt1.totalYforce -= beam.getDampingForce() * math.sin(beam.getCurrentOrientation())
            beam.pt2.totalXforce += beam.getDampingForce() * math.cos(beam.getCurrentOrientation())
            beam.pt2.totalYforce += beam.getDampingForce() * math.sin(beam.getCurrentOrientation())

    def applyGravity(self):
        for beam in self.beams:
            beam.pt1.totalYforce += GRAVITY * beam.pt1.mass 
            beam.pt2.totalYforce += GRAVITY * beam.pt2.mass 

    def boundaryCond(self):
        self.points[1].posX += 30

    def pinAPoint(self):
        if self.pinpoint:
            self.points[0].isPinned = 1
            self.points[0].totalXforce = 0
            self.points[0].totalYforce = 0
            self.points[0].posX = 400
            self.points[0].posY = 400

    def initialize(self):
        for point in self.points:
            point.totalXforce = 0
            point.totalYforce = 0

        self.computeElasticForcesOnPoint()
        self.computeDampingForcesOnPoint()
        self.groundCollision()
        self.applyGravity()

        for point in self.points:
            if point.isPinned:
                point.posX += 0
                point.posY += 0
            else:
                accx = (point.totalXforce)/point.mass 
                accy = (point.totalYforce)/point.mass
                point.vx += accx - point.vx * 0.001
                point.vy += accy - point.vy * 0.001
                point.posX += point.vx
                point.posY += point.vy 

    def groundCollision(self):
        for point in self.points:
            if point.posY >= 700:
                point.posY = 700

    def draw(self):
        self.poly.draw()

#------funzioni generiche di calcolo e conversione------#

#calcolo dei vertici di un poligono regolare
def regularVertCalc(sideNum, radius):
    vertices = []
    k = 0 
    for k in range(k,sideNum):
        vertices.append((radius*math.cos(2*math.pi*k/sideNum) ,radius*math.sin(2*math.pi*k/sideNum)))   
    return vertices

#conversione di un set di vertici in un set di punti
def vertsToPoints(verts: list[tuple], surf: pygame.surface):
    points = []
    for vert in verts: 
        points.append(pointMass(700,vert[0],vert[1],surf))
    return points

#modulo di un vettore
def vectorModulus(p1pos: tuple, p2pos: tuple):
    modulus = math.sqrt(math.pow((p2pos[0] - p1pos[0]),2) + math.pow((p2pos[1] - p1pos[1]),2))
    return modulus

#modulo delle componenti di un vettore
def componentModulus(x, y):
    modulus = math.sqrt(math.pow(x,2) + math.pow(y,2))
    return modulus

#direzione di un vettore
def beamDirection(p1pos: tuple, p2pos: tuple):
    direction = math.atan2((p2pos[1]-p1pos[1]),(p2pos[0]-p1pos[0]))
    return direction

#creo una lista di elementi beam a partire da una lista di punti
#la lista viene creata in modo da fare una linea chiusa
def makeBeamsList(points: list[pointMass], surf: pygame.surface):
    beams = []
    if len(points) == 2:
        beams.append(beamElement(points[0],points[1], surf))
    else:
        for i in range(1,len(points)):
            beams.append(beamElement(points[i-1],points[i], surf))
        beams.append(beamElement(points[len(points)-1],points[0], surf))
    return beams

#combinazione di tutti i beam possibili in un poligono
def makeBeamsCombs(points: list[pointMass], surf: pygame.surface):
    beams = []
    pointCouples = itertools.combinations(points, 2)
    for pointCouple in pointCouples:
        beams.append(beamElement(pointCouple[0],pointCouple[1], surf))
    return beams