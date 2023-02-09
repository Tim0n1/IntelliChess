import math
from config import config
import numpy as np
import matplotlib.pyplot as plt
config = config['dots']
dot_distance_ration_diff = config['minimum_difference_ratio']

class Dot:
    def __init__(self, dot: tuple, position: tuple):
        self._dot = dot
        self._x = dot[0]
        self._y = dot[1]
        self._position = position

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def dot(self):
        return self._dot

    @property
    def position(self):
        return self._position

    @property
    def pos_x(self):
        return self._position[0]

    @property
    def pos_y(self):
        return self._position[1]

    @position.setter
    def position(self, pos):
        self._position = pos


class Dots:
    def __init__(self, dot_objects: list):
        self.dot_objects = dot_objects

    def get_all_dots_from_column(self, n_column):
        dots = []
        for dot in self.dot_objects:
            if dot.pos_x == n_column:
                dots.append(dot)
        return dots

    def get_all_dots_from_row(self, n_row):
        dots = []
        for dot in self.dot_objects:
            #print(dot)
            if dot.pos_y == n_row:
                dots.append(dot)
        return dots

    @staticmethod
    def find_gap_between_dots(x1, y1, x2, y2):
        distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distance

    @staticmethod
    def point_in_circle(center_x, center_y, point_x, point_y, radius=config['radius_of_extinction']):
        distance = Dots.find_gap_between_dots(center_x, center_y, point_x, point_y)
        return distance < radius

    def filter_dots(self):
        objects = self.dot_objects.copy()
        for n, dot1 in enumerate(objects):
            pos_x = dot1.pos_x
            pos_y = dot1.pos_y
            for dot2 in objects[n:len(objects)]:
                if abs(pos_x - dot2.pos_x) == 1 or abs(pos_y - dot2.pos_y) == 1:  # checks if points are adjacent
                    if Dots.point_in_circle(dot1.x, dot1.y, dot2.x, dot2.y):
                        if dot2 in self.dot_objects:
                            self.dot_objects.remove(dot2)

    def apply_dot_coordinates(self):
        unique_coordinates_y = []
        dots_y = self.get_all_dots_from_column(0)
        for dot in dots_y:
            unique_coordinates_y.append(dot.pos_y)
        unique_coordinates_y.sort()
        for dot in self.dot_objects:
            if dot.pos_y not in unique_coordinates_y:
                continue
            new_y = unique_coordinates_y.index(dot.pos_y)
            dot.position = (dot.pos_x, new_y)
        unique_coordinates_x = []
        dots_x = self.get_all_dots_from_row(0)
        for dot in dots_x:
            unique_coordinates_x.append(dot.pos_x)
        unique_coordinates_x.sort()
        print(unique_coordinates_x)
        for dot in self.dot_objects:
            if dot.pos_x not in unique_coordinates_x:
                print('mamkaaaaa muuuuuuuuuuu')
                continue
            new_x = unique_coordinates_x.index(dot.pos_x)
            dot.position = (new_x, dot.pos_y)
        # todo this is bullshit

    def find_distances_h(self, n):
        distances = []
        dots = Dots.get_all_dots_from_row(self, n)
        for n1, dot1 in enumerate(dots):
            for dot2 in dots[n1: len(dots)]:
                if abs(dot1.pos_x - dot2.pos_x) == 1:  # => adjacent
                    distance = Dots.find_gap_between_dots(dot1.x, dot1.y, dot2.x, dot2.y)
                    distances.append([(dot1, dot2), distance])
        return distances

    def find_distances_v(self, n):
        distances = []
        dots = Dots.get_all_dots_from_column(self, n)
        for n, dot1 in enumerate(dots):
            for dot2 in dots[n: len(dots)]:
                if abs(dot1.pos_y - dot2.pos_y) == 1:  # => adjacent
                    distance = Dots.find_gap_between_dots(dot1.x, dot1.y, dot2.x, dot2.y)
                    distances.append([(dot1, dot2), np.round(distance)])
        if not distances:
            return None
        return distances

    def find_most_recurring_distance_horizontal_vertical(self, distances: list):
        if distances is None:
            return None
        r_distances = [0 for _ in range(len(distances))]
        for n, i in enumerate(distances):
            if n + 1 == len(distances):
                break
            for j in distances[n + 1: len(distances)]:
                divisible = min(i[1], j[1])
                divisor = max(i[1], j[1])
                if divisible / divisor >= dot_distance_ration_diff:
                    r_distances[n] += 1
        #print(r_distances)
        legit_d = []
        r = r_distances.index(max(r_distances))
        r = distances[r][1]
        for i in distances:
            if (min(r,i[1])/max(r,i[1])) >= dot_distance_ration_diff:
                legit_d.append(i[1])
        r = np.mean(legit_d)
        return np.round(r)

    def get_number_of_rows_columns(self):
        r = 0
        c = 0
        for i in self.dot_objects:
            if i.pos_y > r:
                r = i.pos_y
            if i.pos_x > c:
                c = i.pos_x
        return r, c

    @staticmethod
    def get_unnecessary_dots(d, mrd, type_line):
        trash_dots = []
        for distance in d:
            if min(distance[1], mrd)/max(distance[1], mrd) < dot_distance_ration_diff:
                trash_dots.append(distance[0][0])
            if min(distance[1], mrd)/max(distance[1], mrd) >= dot_distance_ration_diff:
                break
        for i in range(len(d)):
            if min(d[-i-1][1], mrd)/max(d[-i-1][1], mrd) < dot_distance_ration_diff:
                trash_dots.append(d[-1][0][1])

            if min(d[-i-1][1], mrd)/max(d[-i-1][1], mrd) >= dot_distance_ration_diff:
                break
        return trash_dots

    def add_dots(self, mrd):
        pass


    def filter_dots_via_gap(self):
        r, c = self.get_number_of_rows_columns()
        for row in range(r+1):
            d = self.find_distances_h(row)
            if d == []:
                continue
            mrd = self.find_most_recurring_distance_horizontal_vertical(d)

            trash_dots = Dots.get_unnecessary_dots(d, mrd, 'h')
            for i in trash_dots:
                if i in self.dot_objects:
                    self.dot_objects.remove(i)

        for column in range(c+1):
            d = self.find_distances_v(column)
            if d == []:
                continue
            if d is None:
                continue
            # print(d)
            # plt.plot([i+1 for i in range(len(d))], [i[1] for i in d])
            # plt.show()



