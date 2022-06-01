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

    def draw(self):
        pygame.draw.line(self.surf, self.color, self.pt1pos, self.pt2pos, 2)

    def getCurrentLenght(self):
        curLen = vectorModulus(self.pt1.getPosition(), self.pt2.getPosition()) 
        return curLen

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


##TO DO IMPORTANTISSIMO
#la classe spring mass body dovrà poi implementare un poligono come argomento
#quindi riadattarla in modo simile a quella del rigidbody come argomenti
#perché poi costruirà un body basandosi sui vertici e i beam del poligono
class springMassBody:
    def __init__(self, p1: pointMass, p2: pointMass, surf: pygame.surface):
        self.p1 = p1
        self.p2 = p2
        self.beam = beamElement(p1,p2, surf)
        self.surf = surf
        self.v1 = 0
        self.v2 = 0
        self.gravspeed = 0

    def getBeamRestLenght(self):
        return self.beam.l0

    def getCurrentBeamLenght(self):
        return self.beam.getCurrentLenght()

    def getCurrentBeamLenghtDeprecated(self):
        lenght = vectorModulus(self.p1.getPosition(), self.p2.getPosition())
        return lenght

    def elasticForce(self):
        deltaL = self.getCurrentBeamLenght() - self.beam.l0 
        eForce = abs(deltaL) * self.beam.stiffness 
        if self.getCurrentBeamLenght() > self.beam.l0:
            return -eForce
        else:
            return eForce
    
    def dampingForce(self):
        dForce = [(self.v1)*self.beam.damping, (self.v2)*self.beam.damping]
        return dForce
    
    def boundaryCond(self, bc1, bc2):
        self.p1.posX -= bc1
        self.p1.posY -= bc1
        self.p2.posX += bc2
        self.p2.posY += bc2

    def initialize(self):
        #calcolo della dinamica dei punti
        dampingForce = self.dampingForce()
        acc1 = (-self.elasticForce()-dampingForce[0])/self.p1.mass
        acc2 = (self.elasticForce()-dampingForce[1])/self.p2.mass
        self.v1 += acc1     
        self.v2 += acc2
        #calcolo delle posizioni dei punti
        self.p1.posX += self.v1*math.cos(beamDirection(self.p1.getPosition(),self.p2.getPosition()))
        self.p1.posY += self.v1*math.sin(beamDirection(self.p1.getPosition(),self.p2.getPosition()))
        self.p2.posX += self.v2*math.cos(beamDirection(self.p1.getPosition(),self.p2.getPosition()))
        self.p2.posY += self.v2*math.sin(beamDirection(self.p1.getPosition(),self.p2.getPosition()))
        self.draw()

    def gravity(self):
        self.gravspeed += 0.000004
        self.p1.posY += self.gravspeed
        self.p2.posY += self.gravspeed 

    def draw(self):
        polygon([self.p1, self.p2], self.surf).draw()

######################################################################
class springMassBodyPoly:
    def __init__(self, poly: polygon, surf: pygame.surface):
        self.poly = poly
        self.points = poly.getPoints()
        self.beams = poly.getBeams()
        self.surf = surf
        self.v1 = 0
        self.v2 = 0

    def getBeamRestLenght(self):
        restLenList = []
        for beam in self.beams:
            restLenList.append(beam.l0)
        return restLenList

    def getCurrentBeamLenght(self):
        currLenList = []
        for beam in self.beams:
            lenght = beam.getCurrentLenght()
            currLenList.append(lenght)
        return currLenList

    def elasticForce(self):
        eForces = []
        deltaLs = []
        deltaL = 0
        lens = self.getCurrentBeamLenght()
        restLens = self.getBeamRestLenght()
        for len, restLen in zip(lens,restLens):
            deltaL = len - restLen
            deltaLs.append(deltaL)
        for delt, beam in zip(deltaLs, self.beams):
            eForces.append(delt * beam.stiffness)
        return eForces

    def initialize(self):
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