#https://www.youtube.com/watch?v=qw0oY6Ld-L0&ab_channel=Pythonista_
#https://github.com/Magoninho/3D-projection-tutorial
import numpy as np
from math import *
import math
import cv2

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WIDTH, HEIGHT = 1280, 720
circle_pos = [WIDTH/2,HEIGHT/2]
angle_z = 90
angle = 90
init_z = 30 #cm
square_depth = 8
save_state = []
planes = [[0,3,2],
          [2,6,5],
          [5,4,0],
          [0,3,4],
          [3,2,6],
          [4,5,7]]
not_rendered = True
my_points = []

##calibration constants for camera
#all in cm
Z_MEASUREMENT = 7.8
FOV_H = 9.4
FOV_V = 5.2

#pygame.display.set_caption("3D projection in pygame!")
#screen = pygame.display.set_mode((WIDTH, HEIGHT))
#image_size = (800, 800)  # Define image size
#image = np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)

def init():
    global my_points
    points = []
    

    # all the cube vertices
    points.append(np.matrix([-4.0, -4.0, 4.0])) #0
    points.append(np.matrix([4.0, -4.0, 4.0])) #1
    points.append(np.matrix([4.0,  4.0, 4.0])) #2
    points.append(np.matrix([-4.0, 4.0, 4.0])) #3
    points.append(np.matrix([-4.0, -4.0, -4.0])) #4
    points.append(np.matrix([4.0, -4.0, -4.0])) #5
    points.append(np.matrix([4.0, 4.0, -4.0])) #6
    points.append(np.matrix([-4.0, 4.0, -4.0])) #7

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

    for point in points:
        rotated2d = np.dot(rotation_z, point.reshape((3, 1)))
        rotated2d = np.dot(rotation_y, rotated2d)
        rotated2d = np.dot(rotation_x, rotated2d)
        my_points.append(rotated2d)
     

def connect_points(i, j, points, image, rotated2d):
        #converting points to image land:
        # print("z:", rotated2d[i][2], rotated2d[j][2])
        # plane_width_i = FOV_H * ((init_z - rotated2d[i][2] + (square_depth/2))/Z_MEASUREMENT)
        # plane_height_i = FOV_V * ((init_z - rotated2d[i][2] + (square_depth/2))/Z_MEASUREMENT)

        # plane_width_j = FOV_H * ((init_z - rotated2d[j][2] + (square_depth/2))/Z_MEASUREMENT)
        # plane_height_j = FOV_V * ((init_z - rotated2d[j][2] + (square_depth/2))/Z_MEASUREMENT)

        # image_height, image_width, _ = image.shape

        # pixel_sx = round(((image_width/plane_width_i)* points[i][1]) + (image_width * 0.5))
        # pixel_ex = round(((image_width/plane_width_j)* points[j][1]) + (image_width * 0.5))
        # pixel_sy = round(((image_height/plane_height_i)* points[i][0]) + (image_height * 0.5))
        # pixel_ey = round(((image_height/plane_height_j)* points[j][0]) + (image_height * 0.5))

        # print("Start: (", pixel_sx, pixel_sy, ")", "end: (", pixel_ex, pixel_ey, ")")
        
        # cv2.line(image, (pixel_sx,pixel_sy), (pixel_ex,pixel_ey),(255, 255, 255), 2)

        cv2.line(	        #converting points to image land:
            image, (round(points[i][0]), round(points[i][1])), (round(points[j][0]), round(points[j][1])),(255, 255, 255), 2)
        


def on_plane(x,y,z,pair1,pair2):
     #find normal vector of plane:
        global points_global
        #print(points_global[pair1[0]][0])
        intersection_point = (0,0,0)
        if pair1[0] == pair2[0]:
             intersection_point = (points_global[pair1[0]][0], points_global[pair1[0]][1],points_global[pair1[0]][2])
        if pair1[1] == pair2[0]:
             intersection_point = (points_global[pair1[1]][0], points_global[pair1[1]][1],points_global[pair1[1]][2])
        if pair1[0] == pair2[1]:
             intersection_point = (points_global[pair1[0]][0], points_global[pair1[0]][1],points_global[pair1[0]][2])
        if pair1[1] == pair2[1]:
             intersection_point = (points_global[pair1[1]][0], points_global[pair1[1]][1],points_global[pair1[1]][2])
        #use normal vectors of the 2 lines
        #print("global",points_global)
        #print("pair 1", points_global[pair1[0]][0,0])

        #print(points_global[pair1[0]], points_global[pair1[1]], points_global[pair2[0]], points_global[pair2[1]])
        #print(pair1)
        #print(pair2)
        
        line1_vector = (points_global[pair1[0]][0] -points_global[pair1[1]][0], points_global[pair1[0]][1] -points_global[pair1[1]][1], points_global[pair1[0]][2] -points_global[pair1[1]][2])
        line2_vector =  (points_global[pair2[1]][0] -points_global[pair2[0]][0], points_global[pair2[1]][1] -points_global[pair2[0]][1], points_global[pair2[1]][2] -points_global[pair2[0]][2])

        #print(line1_vector)
        #print(line2_vector)
        normal_vector = np.cross(line1_vector,line2_vector)
        #print(normal_vector)
        #print(intersection_point)
        A = normal_vector[0]
        B = normal_vector[1]
        C = normal_vector[2]
        D = -(normal_vector[0]*intersection_point[0]) - (normal_vector[1]*intersection_point[1]) - (normal_vector[2]*intersection_point[2])

        #print ("abs", abs(A*x + B*y + C*z + D))

        dist = abs(A*x + B*y + C*z + D)/math.sqrt(A**2 + B**2 + C**2)
        #print("dist", dist)
        if dist < 2:
             return True
        return False



def on_cube(x,y,z):
    global not_rendered
    global points_global
    #print(points_global)
    new_z = z - init_z
    
    if not_rendered:
        return False
    
    # Convert the points list to a numpy array for easier manipulation
    points_array = np.array(points_global)
    #print(points_array)

    # Find the maximum and minimum x, y, and z values
    max_x = np.max(points_array[:, 0])
    min_x = np.min(points_array[:, 0])
    max_y = np.max(points_array[:, 1])
    min_y = np.min(points_array[:, 1])
    max_z = np.max(points_array[:, 2])
    min_z = np.min(points_array[:, 2])

    if not (abs(x - max_x) < 2 or (x < max_x and x > min_x) or abs(x - min_x) < 2):
         return False
    if not (abs(y - max_y) < 2 or (y < max_y and y > min_y) or abs(y - min_y) < 2):
         return False
    if not (abs(new_z - max_z) < 2 or (new_z < max_z and new_z > min_z) or abs(new_z - min_z) < 2):
         return False

    num_true = 0
    for plane in planes:
        result = on_plane(x,y,new_z,(plane[0], plane[1]), (plane[0], plane[2]))
        if result:
             #print (plane)
             return result
        #connect_points(p, (p+1) % 4, projected_points, image, rotated2d_global)
        #connect_points(p+4, ((p+1) % 4) + 4, projected_points, image, rotated2d_global)
        #connect_points(p, (p+4), projected_points, image, rotated2d_global)
    return False


def render_cube(image, deltaX, deltaY, deltaZ, deltaA):
    global my_points
    global not_rendered
    global circle_pos
    global angle_z
    global points_global
    global init_z
    scale = 1
    points_global = []
    image_height, image_width, _ = image.shape
    init_z = init_z + deltaZ
    scale_x = (image_width/(FOV_H * (init_z /Z_MEASUREMENT)))
    scale_y =  (image_height/(FOV_V * (init_z/Z_MEASUREMENT)))

    #circle_pos = [round(circle_pos[0] + deltaX * scale_x), round(circle_pos[1] + deltaY * scale_y)]  # x, y
    angle_z = angle_z + deltaA
    #print(circle_pos)
    #circle_pos = [150 + 300, 150 + 450]  # x, y (cube pos)

    
    #print("render", points_global)
    not_rendered = False


    points = []
      # all the cube vertices
    points.append(np.matrix([-4, -4, 4])) #0
    points.append(np.matrix([4, -4, 4])) #1
    points.append(np.matrix([4,  4, 4])) #2
    points.append(np.matrix([-4, 4, 4])) #3
    points.append(np.matrix([-4, -4, -4])) #4
    points.append(np.matrix([4, -4, -4])) #5
    points.append(np.matrix([4, 4, -4])) #6
    points.append(np.matrix([-4, 4, -4])) #7

    
    for i in range(len(my_points)):
       #print("before", my_points[i][0,0])
       #print(my_points[i][0,1])
    #    print(deltaX,deltaY)
    #    print(my_points[i][0,0])
    #    print(my_points[i])
    #    print(my_points[i][1,0])
       my_points[i][0][0] = float(my_points[i][0][0] + deltaX)
       my_points[i][1][0] = float(my_points[i][1][0] + deltaY)
       #print("after", my_points[i][0,0])
       #print(my_points[i][0,1])

    print("my points", my_points)


    projection_matrix = np.matrix([
        [1, 0, 0],
        [0, 1, 0]
    ])

    projected_points = [
        [n, n] for n in range(len(points))
    ]

    rotated2d_global = [
        [n, n, n] for n in range(len(points))
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
    for point in my_points:
        #rotated2d = np.dot(rotation_z, point.reshape((3, 1)))
        #rotated2d = np.dot(rotation_y, rotated2d)
        #rotated2d = np.dot(rotation_x, rotated2d)

        projected2d = np.dot(projection_matrix, point)

        #print("x scale", scale_x)
        #print("y scale", scale_y)
        x = int(projected2d[0][0] * scale_x) + circle_pos[0]
        y = int(projected2d[1][0] * scale_y) + circle_pos[1]
        #print("here:", rotated2d)
        projected_points[i] = [x, y]
        rotated2d_global[i] = [float(point[0][0]), float(point[1][0]), float(point[2][0])]
        #print(rotated2d)
        #points_global.append(np.matrix(rotated2d))
        cv2.circle(image, (round(x),round(y)), radius=5, color=(255, 255, 255), thickness=-1)
        i += 1
    # i = 0
    
    # for point in my_points:
    #     rotated2d = np.dot(rotation_z, point.reshape((3, 1)))
    #     rotated2d = np.dot(rotation_y, rotated2d)
    #     rotated2d = np.dot(rotation_x, rotated2d)
    #     rotated2d_global[i] = [float(rotated2d[0][0]), float(rotated2d[1][0]), float(rotated2d[2][0])]
    #     i +=1

         
    #print("raw:", projected_points)

    points_global = rotated2d_global
    print(points_global)

    for p in range(4):
        connect_points(p, (p+1) % 4, projected_points, image, rotated2d_global)
        connect_points(p+4, ((p+1) % 4) + 4, projected_points, image, rotated2d_global)
        connect_points(p, (p+4), projected_points, image, rotated2d_global)
    
    return projected_points






#import cv2

# Specify the path to your image file
#image_path = '/Users/samdetor/Desktop/download (9).jpeg'

# Load the image
#image = cv2.imread(image_path)
#render_cube(image, 0, 0, 0)
#print(on_cube(-4, -4, 17))
# Check if the image was loaded successfully
# if image is not None:
#     # Display the image
#     cv2.imshow('Loaded Image', image)
#     cv2.waitKey(0)  # Wait for any key press to close the window
#     cv2.destroyAllWindows()  # Close all OpenCV windows
# else:
#     print("Failed to load image.")

