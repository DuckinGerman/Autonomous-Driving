"""
LiDAR point
(x, y, z)

↓

(x, y, z, 1)

↓

4x4 transformation matrix

↓

Camera coordinate
(xc, yc, zc)

"""
import numpy as np
from PIL import Image


def transform_points(points_xyz, transform):
    """
    Transform 3D points using a 4x4 homogeneous transformation matrix.

    Args:
        points_xyz: (3, N)
        transform:  (4, 4)

    Returns:
        transformed_points: (3, N)
    """

    num_points = points_xyz.shape[1]

    points_homogeneous = np.vstack([
        points_xyz,
        np.ones((1, num_points))
    ])

    transformed = transform @ points_homogeneous

    return transformed[:3, :]


def project_to_image(points_camera, intrinsic):
    """
    Project 3D camera-frame points onto the image plane.

    Args:
        points_camera: (3, N)
        intrinsic:     (3, 3)

    Returns:
        pixels: (2, N)
        mask:   points located in front of the camera
    """

    # Camera-frame z must be positive.
    mask = points_camera[2, :] > 0

    points_camera = points_camera[:, mask]

    projected = intrinsic @ points_camera

    # Homogeneous image coordinates -> pixel coordinates.
    projected[0, :] /= projected[2, :]
    projected[1, :] /= projected[2, :]

    return projected[:2, :], mask