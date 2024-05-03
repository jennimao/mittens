import numpy as np
from math import *
import cv2

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WIDTH, HEIGHT = 1280, 720
circle_pos = [WIDTH/2, HEIGHT/2]


#pygame.display.set_caption("3D projection in pygame!")
#screen = pygame.display.set_mode((WIDTH, HEIGHT))
#image_size = (800, 800)  # Define image size
#image = np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)

def connect_points(i, j, points, image):
        cv2.line(
            image, (round(points[i][0]), round(points[i][1])), (round(points[j][0]), round(points[j][1])),(255, 255, 255), 2)


def render_cube(image, deltaX, deltaY):
    global circle_pos
    scale = 100

    circle_pos = [round(circle_pos[0] + deltaX), round(circle_pos[1] + deltaY)]  # x, y
    print(circle_pos)
    #circle_pos = [150 + 300, 150 + 450]  # x, y (cube pos)

    angle = 90

    points = []

    # all the cube vertices
    points.append(np.matrix([-1, -1, 1]))
    points.append(np.matrix([1, -1, 1]))
    points.append(np.matrix([1,  1, 1]))
    points.append(np.matrix([-1, 1, 1]))
    points.append(np.matrix([-1, -1, -1]))
    points.append(np.matrix([1, -1, -1]))
    points.append(np.matrix([1, 1, -1]))
    points.append(np.matrix([-1, 1, -1]))


    projection_matrix = np.matrix([
        [1, 0, 0],
        [0, 1, 0]
    ])

    projected_points = [
        [n, n] for n in range(len(points))
    ]

    rotation_z = np.matrix([
        [cos(angle), -sin(angle), 0],
        [sin(angle), cos(angle), 0],
        [0, 0, 1],
    ])

    rotation_y = np.matrix([
        [cos(angle), 0, sin(angle)],
        [0, 1, 0],
        [-sin(angle), 0, cos(angle)],
    ])

    rotation_x = np.matrix([
        [1, 0, 0],
        [0, cos(angle), -sin(angle)],
        [0, sin(angle), cos(angle)],
    ])
    angle += 0.01

    i = 0
    for point in points:
        rotated2d = np.dot(rotation_z, point.reshape((3, 1)))
        rotated2d = np.dot(rotation_y, rotated2d)
        rotated2d = np.dot(rotation_x, rotated2d)

        projected2d = np.dot(projection_matrix, rotated2d)

        x = int(projected2d[0][0] * scale) + circle_pos[0]
        y = int(projected2d[1][0] * scale) + circle_pos[1]

        projected_points[i] = [x, y]
        cv2.circle(image, (round(x),round(y)), radius=5, color=(255, 255, 255), thickness=-1)
        i += 1

    for p in range(4):
        connect_points(p, (p+1) % 4, projected_points, image)
        connect_points(p+4, ((p+1) % 4) + 4, projected_points, image)
        connect_points(p, (p+4), projected_points, image)
    
    return projected_points

