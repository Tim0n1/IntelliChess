from line_utils import Lines
from dot_utils import *

test_dots = [[(0, 1), (0, 0)], [(5, 1), (0, 1)], [(4, 1), (0, 2)], [(6, 1), (0, 3)], [(12,1), (0,4)]]
d = []
for i in test_dots:
    d.append(Dot(i[0], i[1]))
print(d)
dots = Dots(d)
print(dots.find_most_recurring_distance_horizontal(0))

