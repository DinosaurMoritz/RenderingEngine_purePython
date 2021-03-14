import math
import _ObjLoader
import ConsoleEngine
import time
import logging
from _resources import *

"""x, y, z = 0, 0, 40
sh = 20
p = {  # _                                                 H _____ E
    "A": (x - sh, y - sh, z - sh),  # A                     /    /|
    "B": (x - sh, y + sh, z - sh),  # B                    /    / |
    "C": (x + sh, y + sh, z - sh),  # C                 D /____/A |
    "D": (x + sh, y - sh, z - sh),  # D                   |  G |  | F
    "E": (x - sh, y - sh, z + sh),  # E                   |    | /
    "F": (x - sh, y + sh, z + sh),  # F                  c|____|/ B
    "G": (x + sh, y + sh, z + sh),  # G
    "H": (x + sh, y - sh, z + sh),  # H
}

points = [[p["A"], p["B"], p["C"], p["D"]],
          # [p["E"], p["F"], p["G"], p["H"]],
          # [p["A"], p["E"], p["F"], p["B"]],
          # [p["F"], p["H"], p["C"], p["G"]],
          ]
"""

logging.basicConfig(filename='Projector.log', level=logging.INFO, filemode='a')
logging.info("-" * 100)


class Projector:

    def __init__(self, size, pos=(0, 0, 0), fov=90):
        self.screen = ConsoleEngine.ConsoleEngine(size)
        self.size = size
        self.width, self.height = self.size
        self.fov = fov
        self.near = 1
        self.far = 100
        self.x, self.y, self.z = pos

        self.projectionMatrix = self.getProjectionMatrix()

    def projectPoint(self, v, draw=True):
        v = v[0] + self.x, v[1] + self.y, v[2] + self.z  # Move camera
        if v[2] < 0: return False
        projectedVert = self.multPointMatrix(v, self.projectionMatrix)

        x, y, z = projectedVert
        if x < -1 or x > 1 or y < -1 or y > 1: return False
        x = min(self.width - 1, int(((x + 1) * 0.5 * self.width)))
        y = min(self.height - 1, int(((1 - (y + 1) * 0.5) * self.height)))
        if draw:
            self.screen.drawPixel((x, y))
        return x, y

    def multPointMatrix(self, vin, M):
        x, y, z = vin
        nx = x * M[0][0] + y * M[1][0] + z * M[2][0] + M[3][0]
        ny = x * M[0][1] + y * M[1][1] + z * M[2][1] + M[3][1]
        nz = x * M[0][2] + y * M[1][2] + z * M[2][2] + M[3][2]
        w = x * M[0][3] + y * M[1][3] + z * M[2][3] + M[3][3]

        if w != 1 and w != 0:
            nx /= w
            ny /= w
            nz /= w

        return nx, ny, nz

    def getProjectionMatrix(self):
        scale = 1 / math.tan(self.fov * 0.5 * math.pi / 180)

        return [[scale, 0, 0, 0],
                [0, scale, 0, 0],
                [0, 0, -self.far / (self.far - self.near), -3],
                [0, 0, 0, 0]]

    def display(self):
        self.screen.display()

    @staticmethod
    def movePoint(p, amount):
        return p[0], p[1], p[2] + amount

    @staticmethod
    def flattenList(arr, rounds=1):  # Flattens list round times
        for _ in range(rounds):
            arr = sum(arr, [])
        return arr

    def loadObj(self, name, scaleTo=100):
        self.loader = _ObjLoader.ObjLoader(name, scaleTo)
        self.vertices, self.faces = self.loader.vertices, self.loader.faces

    def drawObj(self):
        for poly in self.faces:
            for triangle in turnIntoTriangles(poly):
                projectedTriangle = [self.projectPoint(self.vertices[p - 1]) for p in triangle]
                if all(projectedTriangle):
                    self.screen.drawTriangle(projectedTriangle, "X")  # )
                    # for p in projectedPoly:
                    #     self.screen.drawPixel(p)


if __name__ == "__main__":
    p = Projector((170, 170), (0, -40, 100), 30)
    # print(p.projectPoint((0, 0, 0)))
    p.loadObj("deer.obj", 130)
    for _ in range(10):
        t1 = time.time()
        p.drawObj()
        p.y -= 2
        p.screen.clearScreen()
        p.display()
        p.screen.clearField()
    logging.info(time.time() - t1)

    input()
