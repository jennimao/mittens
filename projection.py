#https://www.youtube.com/watch?v=qw0oY6Ld-L0&ab_channel=Pythonista_
#https://github.com/Magoninho/3D-projection-tutorial
import numpy as np
from math import *
import cv2

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WIDTH, HEIGHT = 1280, 720
circle_pos = [0,0]
angle_z = 90
angle = 90
init_z = 30 #cm

##calibration constants for camera
#all in cm
Z_MEASUREMENT = 7.8
FOV_H = 9.4
FOV_V = 5.2

#pygame.display.set_caption("3D projection in pygame!")
#screen = pygame.display.set_mode((WIDTH, HEIGHT))
#image_size = (800, 800)  # Define image size
#image = np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)

def connect_points(i, j, points, image):
        #converting points to image land:
        plane_width = FOV_H * (init_z/Z_MEASUREMENT)
        plane_height = FOV_V * (init_z/Z_MEASUREMENT)

        image_height, image_width, _ = image.shape

        pixel_sx = round(((image_width/plane_width)* points[i][0]) + (image_width * 0.5))
        pixel_ex = round(((image_width/plane_width)* points[j][0]) + (image_width * 0.5))
        pixel_sy = round(((image_height/plane_height)* points[i][1]) + (image_height * 0.5))
        pixel_ey = round(((image_height/plane_height)* points[j][1]) + (image_height * 0.5))

        print("Start: (", pixel_sx, pixel_sy, ")", "end: (", pixel_ex, pixel_ey, ")")
        
        cv2.line(image, (pixel_sx,pixel_sy), (pixel_ex,pixel_ey),(255, 255, 255), 2)


def render_cube(image, deltaX, deltaY, deltaA):
    global circle_pos
    global angle_z
    scale = 1

    circle_pos = [round(circle_pos[0] + deltaX), round(circle_pos[1] + deltaY)]  # x, y
    angle_z = angle_z + deltaA
    print(circle_pos)
    #circle_pos = [150 + 300, 150 + 450]  # x, y (cube pos)



    points = []

    # all the cube vertices
    points.append(np.matrix([-4, -4, 4]))
    points.append(np.matrix([4, -4, 4]))
    points.append(np.matrix([4,  4, 4]))
    points.append(np.matrix([-4, 4, 4]))
    points.append(np.matrix([-4, -4, -4]))
    points.append(np.matrix([4, -4, -4]))
    points.append(np.matrix([4, 4, -4]))
    points.append(np.matrix([-4, 4, -4]))


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
        [0, cos(angle_z), -sin(angle_z)],
        [0, sin(angle_z), cos(angle_z)],
    ])

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
    
    print("raw:", projected_points)

    for p in range(4):
        connect_points(p, (p+1) % 4, projected_points, image)
        connect_points(p+4, ((p+1) % 4) + 4, projected_points, image)
        connect_points(p, (p+4), projected_points, image)
    
    return projected_points

