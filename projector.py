import ConsoleEngine
import _ObjLoader
from _resources import *
import time
import math

cube = [
    [[0, 0, 0], [0, 1, 0], [1, 1, 0]],
    [[0, 0, 0], [1, 1, 0], [1, 0, 0]],
    
    [[1, 0, 0], [1, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1], [1, 0, 1]],

    [[1, 0, 1], [1, 1, 1], [0, 1, 1]],
    [[1, 0, 1], [0, 1, 1], [0, 0, 1]],

    [[0, 0, 1], [0, 1, 1], [0, 1, 0]],
    [[0, 0, 1], [0, 1, 0], [0, 0, 0]],

    [[0, 1, 0], [0, 1, 1], [1, 1, 1]],
    [[0, 1, 0], [1, 1, 1], [1, 1, 0]],

    [[1, 0, 1], [0, 0, 1], [0, 0, 0]],
    [[1, 0, 1], [0, 0, 0], [1, 0, 0]],
]


class Projector:
    def __init__(self, size, camera=(0, 0, 10), fov=90):
        self.size = size
        self.width, self.height = self.size
        self.camera = camera
        self.lightDir = (0, 0, -1)
        self.fov = fov
        self.far = 10
        self.near = 1
        self.aspect = self.width / self.height
        self.scalingFactor = 1 / (math.tan(self.fov * 0.5 / 180 * math.pi))
        self.zNormal = self.far / (self.far - self.near)

        self.projectionMatrix = self.getProjectionMatrix()

        self.screen = ConsoleEngine.ConsoleEngine(self.size)

    def projectPoint(self, p):
        pass

    def getProjectionMatrix(self):
        return [
            [self.aspect * self.scalingFactor, 0, 0, 0],
            [0, self.scalingFactor, 0, 0],
            [0, 0, self.zNormal, 1],
            [0, 0, self.near * self.zNormal, 0]
        ]

    def matrixMultiplication(self, p, m):
        w = p[0] * m[0][3] + p[1] * m[1][3] + p[2] * m[2][3] + m[3][3]

        m = [
            p[0] * m[0][0] + p[1] * m[1][0] + p[2] * m[2][0] + m[3][0],
            p[0] * m[0][1] + p[1] * m[1][1] + p[2] * m[2][1] + m[3][1],
            p[0] * m[0][2] + p[1] * m[1][2] + p[2] * m[2][2] + m[3][2]
        ]

        if w != 0 or w != 1:
            m[0] = m[0] / w
            m[1] = m[1] / w
            m[2] = m[2] / w

        return m

    def calcNormal(self, triangle):

        line1 = (
            triangle[1][0] - triangle[0][0],
            triangle[1][1] - triangle[0][1],
            triangle[1][2] - triangle[0][2],
        )

        line2 = (
            triangle[2][0] - triangle[0][0],
            triangle[2][1] - triangle[0][1],
            triangle[2][2] - triangle[0][2],
        )

        normal = [
            line1[1] * line2[2] - line1[2] * line2[1],
            line1[2] * line2[0] - line1[0] * line2[2],
            line1[0] * line2[1] - line1[1] * line2[0]
        ]

        l = -math.sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])

        if l == 0:
            return normal
        return normal[0] / l, normal[1] / l, normal[2] / l

    def projectTriangle(self, triangle):
        # TRANSLATE
        triangle[0][2] += self.camera[2]
        triangle[1][2] += self.camera[2]
        triangle[2][2] += self.camera[2]

        triangle[0][1] += self.camera[1]
        triangle[1][1] += self.camera[1]
        triangle[2][1] += self.camera[1]

        triangle[0][0] += self.camera[0]
        triangle[1][0] += self.camera[0]
        triangle[2][0] += self.camera[0]

        normal = self.calcNormal(triangle)

        if (normal[0] * (triangle[0][0]) +
                normal[1] * (triangle[0][1]) +
                normal[2] * (triangle[0][2]) > 0):
            # PROJECTION
            projectedTriangle = [self.matrixMultiplication(point, self.projectionMatrix) for point in triangle]

            # SCALE INTO VIEW
            projectedTriangle[0][0] = (projectedTriangle[0][0] + 1) * 0.5 * self.width
            projectedTriangle[0][1] = (projectedTriangle[0][1] + 1) * 0.5 * self.height

            projectedTriangle[1][0] = (projectedTriangle[1][0] + 1) * 0.5 * self.width
            projectedTriangle[1][1] = (projectedTriangle[1][1] + 1) * 0.5 * self.height

            projectedTriangle[2][0] = (projectedTriangle[2][0] + 1) * 0.5 * self.width
            projectedTriangle[2][1] = (projectedTriangle[2][1] + 1) * 0.5 * self.height

            projectedTriangle = [(p[0], p[1]) for p in projectedTriangle]

            l = math.sqrt(self.lightDir[0]*self.lightDir[0] + self.lightDir[1]*self.lightDir[1] + self.lightDir[2]*self.lightDir[2])

            #newLightDir = self.lightDir[0] / l, self.lightDir[1] / l, self.lightDir[2] / l

            dotProd = abs((normal[0] * self.lightDir[0] + normal[1] * self.lightDir[1] + normal[2] * self.lightDir[2])) * 255

            shade = self.screen.getShade(dotProd)

            # DRAW
            self.screen.drawTriangle(projectedTriangle, shade)

    def drawCube(self):
        for triangle in cube:
            self.projectTriangle(triangle)

    def drawShip(self):
        obj = _ObjLoader.ObjLoader("mountains.obj", 500)
        faces = obj.faces
        for poly in faces:
            for triangle in turnIntoTriangles(poly):
                self.projectTriangle(triangle)

    def display(self):
        self.screen.display()

    def run(self):
        self.screen.clearField()
        self.drawShip()
        self.screen.clearScreen()
        self.screen.display()


if "__main__" == __name__:
    p = Projector((500, 500), (0, 100, 500))
    t1 = time.time()
    p.run()
    p.display()
    input(1 / (time.time() - t1))
