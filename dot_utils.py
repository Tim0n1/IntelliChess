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
        self._position = position  # (pos_on_h_lines, pos_on_v_lines)
        self.square = None

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

    def get_number_unique_y_pos(self):
        y_values = {}
        for dot in self.dot_objects:
            if dot.pos_y in y_values.keys():
                y_values[dot.pos_y] += 1
            else:
                y_values[dot.pos_y] = 1
        return y_values

    def get_all_dots_from_column(self, n_column):
        dots = []
        for dot in self.dot_objects:
            if dot.pos_x == n_column:
                dots.append(dot)
        return dots

    def get_all_dots_from_row(self, n_row):
        # indexes = list(self.get_number_unique_y_pos().keys())
        #dots = []
        # if indexes == []:
        #     return dots,0
        # print(indexes)
        # print(n_row)
        # n_row = indexes[n_row]
        dots = []
        for dot in self.dot_objects:
            #print(dot)
            if dot.pos_y == n_row:
                dots.append(dot)
        while len(dots) == 0:
            n_row += 1
            if n_row > 9:
                return dots
            for dot in self.dot_objects:
                if dot.pos_y == n_row:
                    dots.append(dot)

        return dots

    def delete_all_dots_from_row(self, n_row):
        dots = self.get_all_dots_from_row(n_row)
        for i in dots:
            self.dot_objects.remove(i)

    @staticmethod
    def find_gap_between_dots(x1, y1, x2, y2):
        distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distance

    # returns true if point is in circle
    @staticmethod
    def point_in_circle(center_x, center_y, point_x, point_y, radius=config['radius_of_extinction']):
        distance = Dots.find_gap_between_dots(center_x, center_y, point_x, point_y)
        return distance < radius

    @staticmethod
    def move_right_on_segment(x0, y0, x1, y1, x2, y2, distance):
        dx = x2 - x1
        dy = y2 - y1
        magnitude = (dx ** 2 + dy ** 2) ** 0.5
        unit_vector = (dx / magnitude, dy / magnitude)
        offset_vector = (unit_vector[0] * distance, unit_vector[1] * distance)
        x = x0 + offset_vector[0]
        y = y0 + offset_vector[1]
        return x, y

    # removes dots that are very close to each other
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

    # resets the dots coordinates (used after filtering)
    def apply_dot_coordinates(self):
        r, c = self.get_number_of_rows_columns()

        for row in range(r):
            dots_x = self.get_all_dots_from_row(row)
            dots_x.sort(key=lambda x: x.x)
            for n1, dot in enumerate(dots_x):
                dot.position = (n1, row)

        for column in range(c):
            dots_y = self.get_all_dots_from_column(column)
            dots_y.sort(key=lambda x: x.y)
            for n2, dot in enumerate(dots_y):
                dot.position = (dot.pos_x, n2)

        l_del = []
        y_values = self.get_number_unique_y_pos()
        for k, v in y_values.items():
            if v <= 2:
                l_del.append(k)
        for i in self.dot_objects:
            if i.pos_y in l_del:
                self.dot_objects.remove(i)

        for row in range(r):
            dots_x = self.get_all_dots_from_row(row)
            dots_x.sort(key=lambda x: x.x)
            for n1, dot in enumerate(dots_x):
                dot.position = (n1, row)


    # find distances of adjacent dots on nth horizontal line
    def find_distances_h(self, n):
        distances = []
        dots = self.get_all_dots_from_row(n)

        for n1, dot1 in enumerate(dots):
            for dot2 in dots[n1+1: len(dots)]:
                if abs(dot1.pos_x - dot2.pos_x) == 1:  # => adjacent
                    distance = Dots.find_gap_between_dots(dot1.x, dot1.y, dot2.x, dot2.y)
                    distances.append([(dot1, dot2), distance])
        return distances

    # find distances of adjacent dots on nth vertical line
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

    # find the most recurring distances in range ratio of 'dot_distance_ration_diff' and returns the average
    def find_most_recurring_distance_horizontal_vertical(self, distances: list):
        if distances is None:
            return None
        r_distances = [0 for _ in range(len(distances))]
        if r_distances == []:
            return None
        for n, i in enumerate(distances):
            if n + 1 == len(distances):
                break
            for j in distances[n + 1: len(distances)]:
                divisible = min(i[1], j[1])
                divisor = max(i[1], j[1])
                if divisor == 0:
                    continue
                if divisible / divisor >= dot_distance_ration_diff:
                    r_distances[n] += 1
        legit_d = []
        r = r_distances.index(max(r_distances))
        r = distances[r][1]
        if r == 0:
            return None
        for i in distances:
            if (min(r, i[1])/max(r, i[1])) >= dot_distance_ration_diff:
                legit_d.append(i[1])
        r = np.mean(legit_d)
        return np.round(r)

    def get_number_of_rows_columns(self):
        c = len(self.get_all_dots_from_row(0))
        r = len(self.get_all_dots_from_column(0))
        return r, c

    # gets dots that are not in 'mrd' ratio
    @staticmethod
    def get_unnecessary_dots(d, mrd):
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

    # adds dots that are part of the squares of the board but are missing
    def add_dots(self, d, mrd):
        x = None
        y = None
        flag = False
        for n, i in enumerate(d):
            if i[1]/0.8 > mrd:

                g = math.floor(i[1]/mrd)
                for _ in range(1, g):
                    if not flag:
                        x0 = i[0][0].x
                        y0 = i[0][0].y
                        flag = True
                    else:
                        x0 = x
                        y0 = y
                    x1 = x0
                    y1 = y0
                    x2 = i[0][1].x
                    y2 = i[0][1].y
                    x, y = Dots.move_right_on_segment(x0, y0, x1, y1, x2, y2, mrd)
                    if math.isnan(x) or math.isnan(y):
                        continue
                    dot = Dot((round(x), round(y)), (0, i[0][0].pos_y))
                    self.dot_objects.append(dot)

    # filter dots that are not part of the board squares
    def filter_dots_via_gap(self):
        r, c = self.get_number_of_rows_columns()
        for row in range(r):
            d = self.find_distances_h(row)
            if d == []:
                continue
            mrd = self.find_most_recurring_distance_horizontal_vertical(d)

            trash_dots = Dots.get_unnecessary_dots(d, mrd)
            for i in trash_dots:
                if i in self.dot_objects:
                    self.dot_objects.remove(i)

        # adding dots
        for row in range(r):
            d = self.find_distances_h(row)
            mrd = self.find_most_recurring_distance_horizontal_vertical(d)
            self.add_dots(d, mrd)

        r, c = self.get_number_of_rows_columns()
        # filtering vertical lines
        for column in range(c):
            d = self.find_distances_v(column)
            if d == []:
                continue
            if d is None:
                continue
            distances = np.asarray([i[1] for i in d], dtype=int)
            if len(distances) < 3:
                continue

            d_indexes1 = []
            # Calculates derivative of the distances between lines
            grad_distances = np.round(np.gradient(distances, 9), 1)

            for i in range(len(grad_distances)):
                if (i + 1) == len(grad_distances):
                    break
                if abs(grad_distances[i] + grad_distances[i+1]) > 2:
                    d_indexes1.append(i)
                else:
                    break
            d_indexes2 = []
            for i in range(len(grad_distances)):
                if abs(-i-2) == len(grad_distances):
                    break
                d1 = grad_distances[-i-1]
                d2 = grad_distances[-i - 2]
                if d1 < 0 and d2 < 0:
                    if abs(grad_distances[-i-1] + grad_distances[-i-2]) > 3:
                        d_indexes2.append(len(grad_distances) - (i+1))
                    else:
                        break
                else:
                    break
            for i in d_indexes1:
                del_rows = []
                dot = d[i][0][0]
                if dot.pos_y in del_rows:
                    continue
                self.delete_all_dots_from_row(dot.pos_y)
                del_rows.append(dot.pos_y)
            for i in d_indexes2:
                # Checks if there are lines on the other side of the board

                    del_rows = []
                    dot = d[i][0][1]
                    if dot.pos_y in del_rows:
                        continue
                    dot = d[i][0][1]
                    self.delete_all_dots_from_row(dot.pos_y)
                    del_rows.append(dot.pos_y)

    def find_dot_by_pos(self, pos_x, pos_y):
        for dot in self.dot_objects:
            if (dot.pos_x == pos_x) and (dot.pos_y == pos_y):
                return dot





