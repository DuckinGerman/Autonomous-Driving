"""
Camera:
translation
rotation
intrinsic

LiDAR:
translation
rotation
"""
from src.geometry.calibration import Calibration


def get_camera_calibration(nusc, sample, camera_name="CAM_FRONT"):
    cam_token = sample["data"][camera_name]

    cam_data = nusc.get("sample_data", cam_token)

    calib_record = nusc.get(
        "calibrated_sensor",
        cam_data["calibrated_sensor_token"]
    )

    return Calibration(
        translation=calib_record["translation"],
        rotation=calib_record["rotation"],
        intrinsic=calib_record["camera_intrinsic"]
    )


def get_lidar_calibration(nusc, sample, lidar_name="LIDAR_TOP"):
    lidar_token = sample["data"][lidar_name]

    lidar_data = nusc.get("sample_data", lidar_token)

    calib_record = nusc.get(
        "calibrated_sensor",
        lidar_data["calibrated_sensor_token"]
    )

    return Calibration(
        translation=calib_record["translation"],
        rotation=calib_record["rotation"]
    )