from ConsoleEngine import ConsoleEngine
from _ObjLoader import ObjLoader
import time
import math


class Projector:
    def __init__(self, _screenSize=(400, 400), _cameraPosition=(0, 0, 20), _fov=90):
        self.screenSize = _screenSize
        self.width, self.height = self.screenSize
        self.screen = ConsoleEngine(self.screenSize)

        self.aspect = self.width / self.height

        self.fov = _fov

        self.scalingFactor = 1 / (math.tan(self.fov * 0.5 / 180 * math.pi))

        self.far = 100
        self.near = 1

        self.zNormal = self.far / (self.far - self.near)

        self.projectionMatrix = self.getProjectionMatrix()

        self.cameraPosition = _cameraPosition

    def projectPoint(self, p):
        p = self.matrixMultiplication(self.addCameraToPoint(p), self.projectionMatrix)
        return ((p[0] + 1) * 0.5 * self.width, (p[1] + 1) * 0.5 * self.height)

    def projectTriangle(self, t):
        t = [self.addCameraToPoint(p) for p in t]
        normal = self.calcTriangleNormal(t)

        if self.dot(normal, t[0]):
            pt = [self.matrixMultiplication(point, self.projectionMatrix) for point in t]
            pt = [((p[0] + 1) * 0.5 * self.width, (p[1] + 1) * 0.5 * self.height) for p in pt]  # (p[0] + 1)
            # z = [p[2] for p in pt]
            # pt = [(p[0], p[1]) for p in pt]

            a = self.calcAngleBetweenVectors(self.cameraPosition, normal)
            if a <= 95:
                shade = [u"\u2591", u"\u2592", u"\u2593", u"\u2588"][round(self.screen.mapFunc(a, 95, 0, 3, 0))]
                self.screen.drawTriangle(pt, shade)
            else:
                shade = [u"\u2591", u"\u2592", u"\u2593", u"\u2588"][round(self.screen.mapFunc(a, 180, 95, 3, 0))]
                self.screen.drawTriangle(pt, shade)

    def calcTriangleNormal(self, triangle):
        v1 = [a - b for a, b in zip(triangle[1], triangle[0])]
        v2 = [a - b for a, b in zip(triangle[2], triangle[0])]
        return self.cross(v1, v2)

    def calcAngleBetweenVectors(self, v1, v2):
        return math.acos(
            self.dot(v1, v2) / (self.calcVectorMagnitude(v1) * self.calcVectorMagnitude(v2))) * 180 / math.pi

    def calcVectorMagnitude(self, v):
        return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

    def addCameraToPoint(self, p):
        return [a + b for a, b in zip(p, self.cameraPosition)]

    def matrixMultiplication(self, p, m):
        w = p[0] * m[0][3] + p[1] * m[1][3] + p[2] * m[2][3] + m[3][3]

        m = [
            p[0] * m[0][0] + p[1] * m[1][0] + p[2] * m[2][0] + m[3][0],
            p[0] * m[0][1] + p[1] * m[1][1] + p[2] * m[2][1] + m[3][1],
            p[0] * m[0][2] + p[1] * m[1][2] + p[2] * m[2][2] + m[3][2]
        ]

        if w != 0 and w != 1:
            m[0] = m[0] / w
            m[1] = m[1] / w
            m[2] = m[2] / w

        return m

    def dot(self, v1, v2):  # Dotproduct
        return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

    def cross(self, v1, v2):  # Crossproduct
        return [v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0]]

    def getProjectionMatrix(self):
        return [
            [self.aspect * self.scalingFactor, 0, 0, 0],
            [0, self.scalingFactor, 0, 0],
            [0, 0, self.zNormal, 1],
            [0, 0, self.near * self.zNormal, 0]
        ]

    def drawObj(self, name, scaleTo=100):
        obj = ObjLoader(name, scaleTo)
        for p in obj.polys:
            for t in p:
                self.projectTriangle(t)
                # print("drawing Triangle", time.time())


if __name__ == "__main__":
    p = Projector(_cameraPosition=(0, 20, 120), _fov=120)
    triangles = [
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
    # triangles = [
    #     # [(0, 0, 0), (10, 10, 0), (10, 0, 0)]
    #  [(0, 0, 0), (0, 10, 10), (1, 0, 10)]
    # ]
    #[p.projectTriangle(triangle) for triangle in triangles]
    # p.calcTriangleNormal([(10, 10, 0), (20, 10, 0), (15, 15, 0)])
    # p.screen.drawPixel(p.projectPoint((0.5, 0.5, 0.1)))
    # p.screen.drawPixel(p.projectPoint((0, 0, 0)))
    # p.screen.drawPixel(p.projectPoint((10, 0, 0)))
    # p.screen.drawPixel(p.projectPoint((0, 10, 0)))
    # p.screen.drawPixel(p.projectPoint((10, 10, 1000)))
    p.drawObj("mountains.obj", 15)
    p.screen.display()
    # test = p.calcAngleBetweenVectors((0, 0, 10), (10, 0, 0))
    # print(test)
    input("Done!")
    # print(p.calcAngleBetweenVectors((10, 0, 0), (0, 1, 0)))
