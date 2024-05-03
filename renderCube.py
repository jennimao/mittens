import numpy as np
import cv2


def renderCube(image):
    h =  720
    w  = 1280
    # Define cube vertices
    # cube_vertices = np.array([[0, 0, 0],
    #                         [1, 0, 0],
    #                         [1, 1, 0],
    #                         [0, 1, 0],
    #                         [0, 0, 1],
    #                         [1, 0, 1],
    #                         [1, 1, 1],
    #                         [0, 1, 1]])

    cube_vertices = np.array([[0, 0, 0, 1],
                          [1, 0, 0, 1],
                          [1, 1, 0, 1],
                          [0, 1, 0, 1],
                          [0, 0, 1, 1],
                          [1, 0, 1, 1],
                          [1, 1, 1, 1],
                          [0, 1, 1, 1]])

    # Define cube edges (connectivity between vertices)
    cube_edges = [(0, 1), (1, 2), (2, 3), (3, 0),
                (4, 5), (5, 6), (6, 7), (7, 4),
                (0, 4), (1, 5), (2, 6), (3, 7)]

    # Create an empty black image
    #image_size = (800, 800)  # Define image size
    #image = np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)


    # Example usage:
    fov = 45.0  # Field of view angle (in degrees)
    aspect_ratio = w/h  # Aspect ratio of the viewport (width / height)
    near = 0.1  # Distance to the near clipping plane
    far = 90.0 # Distance to the far clipping plane

    projection_matrix = perspective_projection_matrix(fov, aspect_ratio, near, far)
    projection_matrix = projection_matrix * 100
    #print(projection_matrix)
    #ratio = 100/40
    # Define projection matrix (for orthographic projection)
    #projection_matrix = np.array([[100, 0, 40],
                                #[0, 100, 40 + 300],#round((300 * (width/height)))],
                                #[0, 0, 1]])
    
    #projection_matrix = np.array([[2/w, 0, -w/2],
                                #[0, 2/h, -h/2],#round((300 * (width/height)))],
                                #[0, 0, 1]])

    # Define rotation matrix (identity matrix for this example)
    rotation_matrix = np.eye(4)

    # Project vertices onto 2D image plane
    projected_vertices = np.dot(cube_vertices, rotation_matrix.T)
    projected_vertices = np.dot(projected_vertices, projection_matrix.T)
    projected_vertices = projected_vertices[:, :2].astype(int)  # Extract only x, y and convert to int

    #save lines
    lines = list()
    # Draw edges on the image
    for edge in cube_edges:
        start_point = tuple(projected_vertices[edge[0]])
        end_point = tuple(projected_vertices[edge[1]])
        lines.append([start_point,end_point])
        cv2.line(image, start_point, end_point, (255, 0, 255), 2)

    print(lines)
    return lines



def perspective_projection_matrix(fov, aspect_ratio, near, far):
    """
    Create a perspective projection matrix.

    Parameters:
        fov (float): Field of view angle (in degrees).
        aspect_ratio (float): Aspect ratio of the viewport (width / height).
        near (float): Distance to the near clipping plane.
        far (float): Distance to the far clipping plane.

    Returns:
        np.ndarray: 4x4 perspective projection matrix.
    """
    f = 1.0 / np.tan(np.radians(fov) / 2)
    z_range = near - far

    projection_matrix = np.array([
        [f / aspect_ratio, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / z_range, 2 * far * near / z_range],
        [0, 0, -1, 0]
    ])

    return projection_matrix


#print("Perspective Projection Matrix:")
#print(projection_matrix)

# Display the image
# cv2.imshow('3D Cube', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()