from _resources import *


"""
class ObjLoader(object):
    def __init__(self, fileName, scaleTo=100):
        self.vertices = []
        self.faces = []

        with open(fileName) as f:
            for line in f.readlines():
                if line[0] == "v" and line[1] == " ": # vertices
                    self.vertices.append([float(c) for c in line[:-1].split(" ")[1:]])
                elif line[0] == "f" and line[1] == " ": # faces
                    self.faces.append([self.vertices[int(c.split("/")[0]) - 1] for c in line[:-1].split(" ")[1:][:-1]])

        if scaleTo:
            d = calcFurthestPointDist(self.vertices, (0, 0, 0))
            factor = calcScaleFactor(d, scaleTo)
            self.vertices = [[c * factor for c in v] for v in self.vertices]
            self.faces = [[[c * factor for c in p] for p in f] for f in self.faces]

class ObjLoader(object):
    def __init__(self, fileName):
        self.vertices = []
        self.faces = []
        ##
        try:
            f = open(fileName)
            for line in f:
                if line[:2] == "v ":
                    index1 = line.find(" ") + 1
                    index2 = line.find(" ", index1 + 1)
                    index3 = line.find(" ", index2 + 1)

                    vertex = (float(line[index1:index2]), float(line[index2:index3]), float(line[index3:-1]))
                    vertex = (round(vertex[0], 2), round(vertex[1], 2), round(vertex[2], 2))
                    self.vertices.append(vertex)

                elif line[0] == "f":
                    string = line.replace("//", "/")
                    ##
                    i = string.find(" ") + 1
                    face = []
                    for item in range(string.count(" ")):
                        if string.find(" ", i) == -1:
                            face.append(string[i:-1])
                            break
                        face.append(string[i:string.find(" ", i)])
                        i = string.find(" ", i) + 1
                    ##
                    self.faces.append(tuple(face))

            f.close()
        except IOError:
            print(".obj file not found.")




class ObjLoader(object):
    def __init__(self, fileName, scaleTo=100):
        self.vertices = []
        self.faces = []
        ##
        try:
            f = open(fileName)
            for line in f:
                if line[:2] == "v ":
                    index1 = line.find(" ") + 1
                    index2 = line.find(" ", index1 + 1)
                    index3 = line.find(" ", index2 + 1)

                    vertex = (float(line[index1:index2]), float(line[index2:index3]), float(line[index3:-1]))
                    vertex = [round(vertex[0], 2), round(vertex[1], 2), round(vertex[2], 2)]
                    self.vertices.append(vertex)

                elif line[0] == "f":
                    string = line.replace("//", "/")
                    ##
                    i = string.find(" ") + 1
                    face = []
                    for item in range(string.count(" ")):
                        if string.find(" ", i) == -1:
                            face.append(string[i:-1])
                            break
                        face.append(string[i:string.find(" ", i)])
                        i = string.find(" ", i) + 1
                    ##
                    face = [c.split("/")[0] for c in face]
                    face = [int(c) for c in face[:-1]]
                    self.faces.append(face)

            if scaleTo:
                d = calcFurthestPointDist(self.vertices, (0, 0, 0))
                factor = calcScaleFactor(d, scaleTo)
                self.vertices = [[c * factor for c in v] for v in self.vertices]

            self.subFaces = [[self.vertices[i - 1] for i in t] for t in self.faces]
            pass
        except IOError:
            raise
        finally:
            f.close()



class ObjLoader:
    def __init__(self, name, scaleTo=100):
        self.name = name

        self.vertices, self.faces = self.load(self.name)

    def load(self, name):
        with open(name) as f:
            linesList = (f.read()).split("\n")

            vertices = []
            faces = []

            #test = linesList[4756]

            #print()
            for i, line in enumerate(linesList):
                try:
                    if line[0] == "v" and line[1] == " ":  # Vertices
                        vertices.append(line[3:].split(" "))
                        continue

                    if line[0] == "f" and line[1] == " ":
                        step1 = line[3:].split(" ")
                        faces.append([v.split("/") for v in step1])
                except:
                    continue

        return vertices, faces

"""


class ObjLoader:
    def __init__(self, name, scaleTo=100):
        self.name = name
        self.scaleTo = scaleTo

        self.polys = self.load()

        if scaleTo:
            d = calcFurthestPointDist(self.vertices, (0, 0, 0))
            factor = calcScaleFactor(d, self.scaleTo)
            self.vertices = [[c * factor for c in v] for v in self.vertices]
            self.faces = [[[c * factor for c in p] for p in f] for f in self.polys]
        else:
            self.vertices = [[c for c in v] for v in self.vertices]
            self.faces = [[[c for c in p] for p in f] for f in self.polys]


    def load(self):
        import re

        flt = r"-?[\d\.]+"
        vertex_pattern = r"v\s+(?P<x>{})\s+(?P<y>{})\s+(?P<z>{})".format(flt, flt, flt)
        face_pattern = r"f\s+((\d+/*\d*/*\d*\s*){3,})"
        # vt_pattern = r"vt\s+(?P<x>{})\s+(?P<y>{})".format(flt, flt)

        self.vertices = []
        self.faces = []
        # self.vt = []

        with open(self.name, "r") as file:
            for line in map(str.strip, file):
                match = re.match(vertex_pattern, line)
                if match is not None:
                    vTuple = list(map(float, match.group("x", "y", "z")))
                    vTuple[1] = -vTuple[1]
                    self.vertices.append(vTuple)
                    continue
                match = re.match(face_pattern, line)
                if match is not None:
                    self.faces.append(
                        list(map(int, [s for s in vertex.split("/") if s])) for vertex in match.group(1).split())
                    continue
                # match = re.match(vt_pattern, line)
                # if match is not None:
                #   t = tuple(map(float, match.group("x", "y")))
                #   t = (t[0],t[1],t[2])

        polys = []
        for n in self.faces:
            sub = []
            for vertex in n:
                sub.append(roundPoint(self.vertices[vertex[
                                                        0] - 1]))  # -1 because in the OBJ spec, collections start at index 1 rather than 0
            polys.append(sub)

        return list({tuple(sorted(x)) for x in polys})



if __name__ == "__main__":
    l = ObjLoader("ship.obj")
    print()
