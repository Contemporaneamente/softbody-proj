import math
import pygame
#itertools.combination servià poi per fare tutte le connessioni necessarie tra i punti
import itertools

#------classi------#

#massa puntiforme
class pointMass:
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
    def draw(self):
        pygame.draw.circle(self.surf, self.color, [self.posX, self.posY], self.radius)
    def getPosition(self):
        return (self.posX, self.posY)

#elemento di connessione tra due punti
class beamElement:
    def __init__(self, pt1: pointMass, pt2: pointMass, surf: pygame.surface):
        self.pt1 = pt1
        self.pt2 = pt2
        self.pt1pos = pt1.getPosition()
        self.pt2pos = pt2.getPosition()
        self.color = [0,10,10]
        self.surf = surf
        self.stiffness = 0.00005
        self.damping = 0.01
        self.l0 = vectorModulus(pt1.getPosition(), pt2.getPosition())

    def getCurrentLenght(self):
        curLen = vectorModulus(self.pt1.getPosition(), self.pt2.getPosition()) 
        return curLen

    def getCurrentOrientation(self):
        curOr = beamDirection(self.pt1.getPosition(), self.pt2.getPosition())
        return curOr
    
    def getElasticForce(self):
        deltaL = self.getCurrentLenght() - self.l0 
        eForce = abs(deltaL) * self.stiffness 
        if self.getCurrentLenght() > self.l0:
            return -eForce
        else:
            return eForce

    def draw(self):
        pygame.draw.line(self.surf, self.color, (self.pt1.posX, self.pt1.posY), (self.pt2.posX, self.pt2.posY), 2)

#poligono generico
class polygon:
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
class rigidBody:
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
class springMassBody:
    def __init__(self, poly: polygon, surf: pygame.surface):
        self.poly = poly
        self.points = poly.getPoints()
        self.beams = poly.getBeams()
        self.surf = surf

    def computeForcesOnPoint(self):
        for beam in self.beams:
            beam.pt1.totalXforce -= beam.getElasticForce() * math.cos(beam.getCurrentOrientation())
            beam.pt1.totalYforce -= beam.getElasticForce() * math.sin(beam.getCurrentOrientation())
            beam.pt2.totalXforce += beam.getElasticForce() * math.cos(beam.getCurrentOrientation())
            beam.pt2.totalYforce += beam.getElasticForce() * math.sin(beam.getCurrentOrientation())
        
    def boundaryCond(self):
        self.points[1].posX += 10

    def boundaryCond2P(self):
        self.points[0].posX -= 10
        self.points[0].posY -= 10
        self.points[1].posX += 10
        self.points[1].posY += 10

    def initialize(self):
        self.computeForcesOnPoint()

        for point in self.points:
            accx = point.totalXforce/point.mass
            accy = point.totalYforce/point.mass
            point.vx += accx
            point.vy += accy
            point.posX += accx
            point.posY += accy

        self.draw()

    def draw(self):
        self.poly.draw()

#------funzioni generice di calcolo e conversione------#

#calcolo dei vertici di un poligono regolare
def regularVertCalc(sideNum, radius):
    vertices = []
    k = 0 
    for k in range(k,sideNum):
        vertices.append((radius*math.cos(2*math.pi*k/sideNum) + 200 ,radius*math.sin(2*math.pi*k/sideNum) + 200))   
    return vertices

#conversione di un set di vertici in un set di punti
def vertsToPoints(verts: list[tuple], surf: pygame.surface):
    points = []
    for vert in verts: 
        points.append(pointMass(10,vert[0],vert[1],surf))
    return points

#modulo di un vettore
def vectorModulus(p1pos: tuple, p2pos: tuple):
    modulus = math.sqrt(math.pow((p2pos[0] - p1pos[0]),2) + math.pow((p2pos[1] - p1pos[1]),2))
    return modulus

#direzione di un vettore
def beamDirection(p1pos: tuple, p2pos: tuple):
    direction = math.atan2((p2pos[1]-p1pos[1]),(p2pos[0]-p1pos[0]))
    return direction

#creo una lista di elementi beam a partire da una lista di punti
#la lista viene creata in modo da fare una linea chiusa
def makeBeamsList(points: list[pointMass], surf: pygame.surface):
    beams = []
    for i in range(1,len(points)):
        beams.append(beamElement(points[i-1],points[i], surf))
    beams.append(beamElement(points[len(points)-1],points[0], surf))
    return beams

def makeBeamsCombs(points: list[pointMass], surf: pygame.surface):
    beams = []
    pointCouples = itertools.combinations(points, 2)
    for pointCouple in pointCouples:
        beams.append(beamElement(pointCouple[0],pointCouple[1], surf))
    return beams