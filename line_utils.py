import time

from dot_utils import Dot, Dots
import cv2
import matplotlib.pyplot as plt
from config import config, res_x, res_y


m_horizontal = config['lines']['max_horizontal_line_slope']
m_vertical = config['lines']['max_vertical_line_threshold']


class Line:
    def __init__(self, line):
        self._line = line
        self._x1 = line[0][0]
        self._x2 = line[1][0]
        self._y1 = line[0][1]
        self._y2 = line[1][1]

    @property
    def x1(self):
        return self._x1

    @property
    def x2(self):
        return self._x2

    @property
    def y1(self):
        return self._y1

    @property
    def y2(self):
        return self._y2

    @property
    def line(self):
        return self._line

    @line.setter
    def line(self, line):
        self._line = line

    @x1.setter
    def x1(self, x1):
        self._x1 = x1

    @x2.setter
    def x2(self, x2):
        self._x2 = x2

    @y1.setter
    def y1(self, y1):
        self._y1 = y1

    @y2.setter
    def y2(self, y2):
        self._y2 = y2

    def get_slope(self):
        if self.x2 - self.x1 == 0:
            return None
        m = (self.y2 - self.y1) / (self.x2 - self.x1)
        return m

    def normalize_line_coordinates(self, xmin=0, xmax=res_x, ymin=0, ymax=res_y):
        # Calculate the slope of the line
        x1 = None
        y1 = None
        x2 = None
        y2 = None
        m = self.get_slope()
        if m is None:
            return None
        if abs(m) <= m_horizontal:
            x1, y1 = Lines.line_intersection(self.line, ((xmin, ymin), (xmin, ymax)))
            # intersection with the other horizontal line
            x2, y2 = Lines.line_intersection(self.line, ((xmax, ymin), (xmax, ymax)))
        # intersection with x-axis
        elif abs(m) >= m_vertical:
            x1, y1 = Lines.line_intersection(self.line, ((xmin, ymin), (xmax, ymin)))
            # intersection with the other horizontal line
            x2, y2 = Lines.line_intersection(self.line, ((xmin, ymax), (xmax, ymax)))
        if (x1 is None) or (y1 is None) or (x2 is None) or (y2 is None):
            self.line = None
            return None

        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.line = [(x1, y1), (x2, y2)]


class Lines:

    def __init__(self, lines: list):
        self.l1 = lines
        self.line_objects = []
        self.intersection_dots = []

    def get_line_objects(self):

        for line in self.l1:
            line_object = Line(line)
            line_object.normalize_line_coordinates()
            if line_object.line is None:
                continue
            self.line_objects.append(line_object)

    def filter_dots(self):
        dots = Dots(self.intersection_dots)
        dots.filter_dots()
        dots.filter_dots_via_gap()
        dots.apply_dot_coordinates()
        filtered = dots.dot_objects
        self.intersection_dots = filtered
        #time.sleep(0.05)

    def find_lines_intersections(self):
        horizontal, vertical = Lines.find_vertical_and_horizontal_lines(self)
        for ny, h in enumerate(horizontal):
            for nx, v in enumerate(vertical):
                dot = Lines.line_intersection(h.line, v.line)
                if dot is None:
                    continue
                else:
                    self.intersection_dots.append(Dot(dot, (ny, nx)))

    def find_vertical_and_horizontal_lines(self):
        vertical_lines = []
        horizontal_lines = []
        for line in self.line_objects:
            if line.get_slope() is None:
                continue
            if abs(line.get_slope()) <= m_horizontal:
                horizontal_lines.append(line)
            else:
                if abs(line.get_slope()) >= m_vertical:
                    vertical_lines.append(line)
        horizontal_lines.sort(key=lambda x: x.y1)
        vertical_lines.sort(key=lambda x: x.x1)
        self.line_objects = horizontal_lines + vertical_lines
        return horizontal_lines, vertical_lines

    # Finds if line intersect
    @staticmethod
    def line_intersection(line1: tuple, line2: tuple):
        (x1, y1), (x2, y2) = line1
        (x3, y3), (x4, y4) = line2
        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if denom == 0:  # parallel
            return None, None
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
        if ua < 0 or ua > 1:  # out of range
            return None, None
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
        if ub < 0 or ub > 1:  # out of range
            return None, None
        x = x1 + ua * (x2 - x1)
        y = y1 + ua * (y2 - y1)
        if (x >= 0) and (x <= 640) and (y >= 0) and (y <= 640):
            return round(x), round(y)
        else:
            return None, None

    def find_the_highest_and_lowest_horizontal_line(self):
        flag = False
        min_y = None
        max_y = None
        for line in Lines.find_vertical_and_horizontal_lines(self)[0]:
            if not flag:
                min_y = line
                max_y = line
                flag = True
            if line.y1 < min_y.y1:
                min_y = line
            if line.y1 > max_y.y1:
                max_y = line
        if (min_y is None) or (max_y is None):
            return None

        return min_y, max_y

    def find_the_rightmost_and_the_leftmost_line(self):
        flag = False
        min_x = None
        max_x = None
        for line in Lines.find_vertical_and_horizontal_lines(self)[1]:
            if not flag:
                min_x = line
                max_x = line
                flag = True
            if line.x1 < min_x.x1:
                min_x = line
            if line.x1 > max_x.x1:
                max_x = line
        if (min_x is None) or (max_x is None):
            return None
        return min_x, max_x


    def find_borders(self):
        horizontal = Lines.find_the_highest_and_lowest_horizontal_line(self)
        vertical = Lines.find_the_rightmost_and_the_leftmost_line(self)
        if (horizontal is None) or (vertical is None):
            return None
        min_h = horizontal[0]
        max_h = horizontal[1]
        min_v = vertical[0]
        max_v = vertical[1]
        return [min_h, max_h, min_v, max_v]





def plot1(l):
    for n, line in enumerate(l):
        print(n)
        x = [line.x1, line.x2]
        y = [line.y1, line.y2]
        cv2.line(img, (x[0], y[0]), (x[1], y[1]), (0, 0, 255), 2)

    plt.imshow(img)
    plt.show()
    cv2.imshow('d', img)
    cv2.waitKey(0)
def plot_lines(l):
    for n,line in enumerate(l):
        x = [line.line[0][0], line.line[1][0]]
        y = [line.line[0][1], line.line[1][1]]
        cv2.line(img, (x[0], y[0]), (x[1], y[1]), (0, 0, 255), 2)

        #print(y[0]+'------->>>')
        plt.plot(x, y)
        #plt.text(x[0], y[0],  size=10)
    plt.show()
    # cv2.imshow('d',img)
    # cv2.waitKey(0)

# lines.normalize_lines()
#
# filtred = lines.filter_lines()
# plot_lines(lines.filter_lines_via_gap('x1'))
# # plot_lines(filtred[0])
# plot_lines(lines.filter_lines_via_gap('y1'))
# plot_lines(filtred[1])
# filtred1 = filtred[0] + filtred[1]

# line = Line([(5, -250), (320, 320)])
# print(line.normalize_line_coordinates())
