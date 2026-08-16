import numpy as np
from pyquaternion import Quaternion


def calibration_to_matrix(calibration):
    """
    Convert sensor calibration into a 4x4 homogeneous transform.

    The resulting matrix transforms points from the sensor frame
    into the ego vehicle frame.
    """

    rotation_matrix = Quaternion(
        calibration.rotation
    ).rotation_matrix

    transform = np.eye(4)

    transform[:3, :3] = rotation_matrix
    transform[:3, 3] = calibration.translation

    return transform


def invert_transform(transform):
    """
    Invert a 4x4 rigid-body transformation matrix.
    """

    rotation = transform[:3, :3]
    translation = transform[:3, 3]

    inverse = np.eye(4)

    inverse[:3, :3] = rotation.T
    inverse[:3, 3] = -rotation.T @ translation

    return inverse