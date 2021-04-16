import logging
import os
import time


class ConsoleEngine:

    def __init__(self, dimensions=(948, 506), fontSize=2):
        changeFontSize(fontSize)

        self.width, self.height = dimensions
        os.system(f'mode con: cols={self.width + 4} lines={self.height + 4}')
        self.shade = {
            "light": u"\u2591",
            "medium": u"\u2592",
            "dark": u"\u2593",
            "full": u"\u2588",
            "X": "X",
            "x": "x"
        }
        self.detailedShade = [u"\u2588"] + list(
            "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")

        self.red = [22, 106, 18, 66, 172, 170, 118, 44, 192]
        self.yellow = [102, 80, 96, 206, 184, 210, 176]
        self.blue = [14, 62, 254]
        self.green = [70, 166, 124, 244]
        self.gray = [88, 28, 158, 58, 132, 50, 236, 188]

        self.field = [[" " for x in range(self.width)] for y in range(self.height)]
        logging.basicConfig(filename='ConsoleDraw.log', level=logging.INFO, filemode='w',
                            format='%(levelname)s - %(message)s', )

    def clearField(self):
        self.field = [[" " for x in range(self.width)] for y in range(self.height)]

    @staticmethod
    def clearScreen():
        os.system('cls')

    def clear(self):
        self.clearScreen()
        self.clearField()

    @staticmethod
    def roundPoint(p, r=0):
        return tuple([int(round(x, r)) for x in p])

    @staticmethod
    def mapFunc(value, start1, stop1, start2,
                stop2):  # Maps a value from a range ont a nother value from a different range
        return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))

    @staticmethod
    def turnIntoTriangles(poly):
        return [(poly[0], b, c) for b, c in zip(poly[1:], poly[2:])]

    def getLowResShade(self, value):
        return [" ", u"\u2591", u"\u2592", u"\u2593", u"\u2588"][
            round(self.mapFunc(value, 255, 0, 4, 0))]

    def getShade(self, value):
        return self.detailedShade[
            round(self.mapFunc(value, 255, 0, 69, 0))]

    def onScreen(self, pixel):
        if 0 < pixel[0] < self.width and 0 < pixel[1] < self.height:
            return True
        return False

    def drawPixel(self, xy, shade=u"\u2588"):
        if self.onScreen(xy):
            self._drawPixel(xy, shade)

    def _drawPixel(self, xy, shade=u"\u2588"):
        x, y = xy
        self.field[round(y)][round(x)] = shade

    def drawLine(self, p1, p2, shade=u"\u2588", draw=True):
        p1 = self.roundPoint(p1)
        p2 = self.roundPoint(p2)

        x0, y0 = p1
        x1, y1 = p2

        line = []

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                line.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                line.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        line.append((x, y))

        line = list(set(line))
        if draw:
            for c in line:
                self.drawPixel(c, shade)
        return line

    def drawLevelLine(self, _start, _end, y, shade=u"\u2588"):
        start = round(min(_start, _end))
        end = round(max(_end, _start))
        for x in list(range(start, end)):
            self.drawPixel((x, y), shade)

    @staticmethod
    def collinear(p1, p2, p3):
        a = p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])
        return a == 0

    def drawTriangleOutline(self, triangle, shade=u"\u2588"):
        self.drawLine(triangle[0], triangle[1], shade)
        self.drawLine(triangle[1], triangle[2], shade)
        self.drawLine(triangle[2], triangle[0], shade)

    def fillBottomFlatTriangle(self, v1, v2, v3, shade=u"\u2588"):
        try:
            invslope1 = (v2[0] - v1[0]) / (v2[1] - v1[1])
            invslope2 = (v3[0] - v1[0]) / (v3[1] - v1[1])

        except ZeroDivisionError:
            self.drawLine(v1, v3)
            return

        curx1 = v1[0]
        curx2 = v1[0]

        for scanlineY in range(int(v1[1]), int(v2[1])):
            self.drawLevelLine(curx2, curx1, scanlineY, shade)  # drawLine((curx1, scanlineY), (curx2, scanlineY))
            curx1 += invslope1
            curx2 += invslope2

    def fillTopFlatTriangle(self, v1, v2, v3, shade=u"\u2588"):
        invslope1 = (v3[0] - v1[0]) / (v3[1] - v1[1])
        invslope2 = (v3[0] - v2[0]) / (v3[1] - v2[1])

        curx1 = v3[0]
        curx2 = v3[0]

        for scanlineY in list(range(int(v1[1]), int(v3[1])))[::-1]:  # --
            self.drawLevelLine(curx1, curx2, scanlineY, shade)
            curx1 -= invslope1
            curx2 -= invslope2

    def drawTriangle(self, triangle, shade=u"\u2588"):
        if not self.collinear(*triangle):
            triangle = sorted(triangle, key=lambda x: x[1])
            v1, v2, v3 = triangle

            if v2[1] == v3[1]:
                self.fillBottomFlatTriangle(v1, v2, v3, shade)

            elif v1[1] == v2[1]:
                self.fillTopFlatTriangle(v1, v2, v3, shade)

            else:
                v4 = (v1[0] + ((v2[1] - v1[1]) / (v3[1] - v1[1])) * (v3[0] - v1[0])), v2[1]
                self.fillBottomFlatTriangle(v1, v2, v4, shade)
                self.fillTopFlatTriangle(v2, v4, v3, shade)

        else:
            triangle = sorted(triangle, key=lambda x: x[1])
            self.drawLine(triangle[0], triangle[2])

    def drawPoly(self, poly, shade=u"\u2588"):
        [self.drawTriangle(t, shade) for t in self.turnIntoTriangles(poly)]

    def display(self, border=False):
        try:
            if border:
                filledLines = "".join([border for n in range(self.width + 2)])
                everythingElse = "\n".join([border + "".join(self.field[n]) + border for n in range(len(self.field))])
                print(filledLines + "\n" + everythingElse + "\n" + filledLines)
            else:
                print("\n".join(["".join(r) for r in self.field]))
        except Exception as e:
            logging.error("Failed Printing Field")
            logging.error(str(e))

    def getKeyboardInput(self):
        pass


def changeFontSize(size=2):
    from ctypes import POINTER, WinDLL, Structure, sizeof, byref
    from ctypes.wintypes import BOOL, SHORT, WCHAR, UINT, ULONG, DWORD, HANDLE

    LF_FACESIZE = 32
    STD_OUTPUT_HANDLE = -11

    class COORD(Structure):
        _fields_ = [
            ("X", SHORT),
            ("Y", SHORT),
        ]

    class CONSOLE_FONT_INFOEX(Structure):
        _fields_ = [
            ("cbSize", ULONG),
            ("nFont", DWORD),
            ("dwFontSize", COORD),
            ("FontFamily", UINT),
            ("FontWeight", UINT),
            ("FaceName", WCHAR * LF_FACESIZE)
        ]

    kernel32_dll = WinDLL("kernel32.dll")

    get_last_error_func = kernel32_dll.GetLastError
    get_last_error_func.argtypes = []
    get_last_error_func.restype = DWORD

    get_std_handle_func = kernel32_dll.GetStdHandle
    get_std_handle_func.argtypes = [DWORD]
    get_std_handle_func.restype = HANDLE

    get_current_console_font_ex_func = kernel32_dll.GetCurrentConsoleFontEx
    get_current_console_font_ex_func.argtypes = [HANDLE, BOOL, POINTER(CONSOLE_FONT_INFOEX)]
    get_current_console_font_ex_func.restype = BOOL

    set_current_console_font_ex_func = kernel32_dll.SetCurrentConsoleFontEx
    set_current_console_font_ex_func.argtypes = [HANDLE, BOOL, POINTER(CONSOLE_FONT_INFOEX)]
    set_current_console_font_ex_func.restype = BOOL

    stdout = get_std_handle_func(STD_OUTPUT_HANDLE)
    font = CONSOLE_FONT_INFOEX()
    font.cbSize = sizeof(CONSOLE_FONT_INFOEX)

    font.dwFontSize.X = size
    font.dwFontSize.Y = size

    set_current_console_font_ex_func(stdout, False, byref(font))


if __name__ == "__main__":
    f = ConsoleEngine((250, 250))
    # f.drawTriangle(((3, 6), (20, 23), (5, 16)))
    # f.drawLine((0, 0), (948, 506))
    # f.drawBigPixel((10, 10), 30)
    # f.drawPoly([(0, 0), (50, 2), (60, 30), (57, 70), (20, 80), (12, 60)])
    # for p in [(2, 3), (50, 2), (57, 70), (12, 60)]:
    #    f.drawPixel(p)
    # print(f.turnIntoTriangles([("a"),("b"),("c"),("d")]))b
    f.drawTriangle([(34, 59), (85, 4), (101, 156)])
    #f.drawTriangle([(0, 0), (0, 100), (150, 100)])
    # f.drawLevelLine(14, 60, 30)
    # f.display(f.shade["full"])

    f.display()
    input("[DONE!]")
