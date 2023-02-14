import cv2
import numpy as np
from line_utils import Lines
from config import config

config = config['hough_transform']
coordinate_value_threshold = config['coordinate_value_threshold']

def convert_image_to_canny(img):
    # Convert to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Blur the image for better edge detection
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)

    edges = cv2.Canny(image=img_blur,
                      threshold1=config['canny_threshold_1'],
                      threshold2=config['canny_threshold_2'])
    return edges


def hough(img):
    edges = convert_image_to_canny(img)
    # cv2.imwrite('edgesDetected_cv.jpg', edges)
    # cv2.imshow('Edged',edges)
    #cv2.waitKey()

    # Hough transform
    lines = cv2.HoughLines(edges, 1, np.pi / 180, config['min_line_votes'])
    if lines is None:
        return None

    # The below for loop runs till r and theta values
    # are in the range of the 2d array
    lines_drawn = []
    # for line in lines:
    #     x1, y1, x2, y2 = line[0]
    for r_theta in lines:
        arr = np.array(r_theta[0], dtype=np.float64)
        r, theta = arr
        # Stores the value of cos(theta) in a
        a = np.cos(theta)

        # Stores the value of sin(theta) in b
        b = np.sin(theta)

        # x0 stores the value rcos(theta)
        x0 = a * r

        # y0 stores the value rsin(theta)
        y0 = b * r

        # x1 stores the rounded off value of (rcos(theta)-1000sin(theta))
        x1 = int(x0 + coordinate_value_threshold * (-b))

        # y1 stores the rounded off value of (rsin(theta)+1000cos(theta))
        y1 = int(y0 + coordinate_value_threshold * (a))

        # x2 stores the rounded off value of (rcos(theta)+1000sin(theta))
        x2 = int(x0 - coordinate_value_threshold * (-b))

        # y2 stores the rounded off value of (rsin(theta)-1000cos(theta))
        y2 = int(y0 - coordinate_value_threshold * (a))

        lines_drawn.append([(x1, y1), (x2, y2)])
    squares = None
    borders = None
    lines = Lines(lines_drawn)
    lines.get_line_objects()
    lines.find_lines_intersections()
    lines.filter_dots()
    squares = lines.initialize_chess_squares()
    borders = lines.find_borders()
    if squares is not None:
        print(len(squares))
        return squares, 1
    elif (borders is not None) and (lines.intersection_dots is not None):
        return [lines.intersection_dots, borders]
    elif lines.intersection_dots is not None:
        return [lines.intersection_dots, []]
    else:
        return None

    # All the changes made in the input image are finally
    # written on a new image houghlines.jpg
    # cv2.imwrite('linesDetected.jpg', img)
    # print(lines_drawn)