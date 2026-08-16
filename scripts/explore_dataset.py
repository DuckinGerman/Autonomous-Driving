from nuscenes.nuscenes import NuScenes
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from nuscenes.utils.data_classes import LidarPointCloud
from nuscenes.utils.data_classes import RadarPointCloud

from src.dataset.nuscenes_parser import (
    get_camera_calibration,
    get_lidar_calibration
)

from src.geometry.transform import (
    calibration_to_matrix,
    invert_transform
)

from src.geometry.projection import (
    transform_points,
    project_to_image
)

def main():
    nusc = NuScenes(
        version="v1.0-mini",
        dataroot="datasets/nuscenes",
        verbose=True
    )

    
    # print("\n===== nuScenes Dataset Info =====")
    # print(f"Number of scenes:  {len(nusc.scene)}")
    # print(f"Number of samples: {len(nusc.sample)}")


    # sample = nusc.sample[0]

    scene = nusc.scene[0]

    sample_token = scene["first_sample_token"]

    frame_idx = 0

    while sample_token != "":
        
        sample = nusc.get("sample", sample_token)

        # ===========================
        # 这里放你原来所有的代码
        #
        # Camera
        # LiDAR
        # Calibration
        # Projection
        # Depth Coloring
        #
        # ===========================

        # camera
        cam_token = sample["data"]["CAM_FRONT"]

        cam_data = nusc.get("sample_data", cam_token)

        # print("\n===== CAM_FRONT Sample Data =====")
        # print("Filename:", cam_data["filename"])
        # print("Timestamp:", cam_data["timestamp"])
        # print("Calibrated sensor token:", cam_data["calibrated_sensor_token"])
        # print("Ego pose token:", cam_data["ego_pose_token"])

        cam_path = nusc.get_sample_data_path(cam_token)

        # print("\nFull camera path:")
        # print(cam_path)
        # image = Image.open(cam_path)

        # plt.figure(figsize=(12, 6))
        # plt.imshow(image)
        # plt.title("nuScenes - CAM_FRONT")
        # plt.axis("off")
        # plt.savefig("outputs/v1/cam_front.png", bbox_inches="tight")

        # lidar
        lidar_token = sample["data"]["LIDAR_TOP"]
        lidar_path = nusc.get_sample_data_path(lidar_token)

        print("\n===== LIDAR_TOP =====")
        print("Path:", lidar_path)

        lidar_pc = LidarPointCloud.from_file(lidar_path)

        print("Point cloud shape:", lidar_pc.points.shape)
        print("Number of points:", lidar_pc.points.shape[1])

        # bev
        plt.figure(figsize=(8, 8))

        plt.scatter(
            lidar_pc.points[0, :],
            lidar_pc.points[1, :],
            s=0.5
        )

        plt.xlabel("X [m]")
        plt.ylabel("Y [m]")
        plt.title("nuScenes LIDAR_TOP - Bird's Eye View")
        plt.axis("equal")
        plt.grid(True)

        plt.savefig(
            "outputs/v1/lidar_bev.png",
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()

        # calibration cam
        calib = nusc.get(
                "calibrated_sensor",
                cam_data["calibrated_sensor_token"]
            )
        
        print("\n===== Camera Calibration =====")

        print("Translation:")
        print(calib["translation"])

        print("\nRotation (Quaternion):")
        print(calib["rotation"])

        print("\nIntrinsic:")
        print(np.array(calib["camera_intrinsic"]))

        # ego calibration
        ego_pose = nusc.get(
            "ego_pose",
            cam_data["ego_pose_token"]
            )

        print("\n===== Ego Pose =====")

        print("Translation:")
        print(ego_pose["translation"])

        print("\nRotation (Quaternion):")
        print(ego_pose["rotation"])

        # radar
        radar_token = sample["data"]["RADAR_FRONT"]
        radar_path = nusc.get_sample_data_path(radar_token)

        radar_pc = RadarPointCloud.from_file(radar_path)

        print("\n===== RADAR_FRONT =====")
        print("Path:", radar_path)
        print("Radar shape:", radar_pc.points.shape)
        print("Number of radar points:", radar_pc.points.shape[1])

        # src test
        camera_calib = get_camera_calibration(nusc, sample)
        lidar_calib = get_lidar_calibration(nusc, sample)

        print("\n===== Camera Calibration Object =====")
        print(camera_calib)

        print("\n===== LiDAR Calibration Object =====")
        print(lidar_calib)

        # transform test
        T_ego_camera = calibration_to_matrix(camera_calib)
        T_ego_lidar = calibration_to_matrix(lidar_calib)

        T_camera_ego = invert_transform(T_ego_camera)

        print("\n===== Camera -> Ego =====")
        print(T_ego_camera)

        print("\n===== LiDAR -> Ego =====")
        print(T_ego_lidar)

        print("\n===== Ego -> Camera =====")
        print(T_camera_ego)

        print("\n===== Inverse Check =====")
        print(T_camera_ego @ T_ego_camera)


        # projection test
        T_camera_lidar = T_camera_ego @ T_ego_lidar
        print("\n===== LiDAR -> Camera =====")
        print(T_camera_lidar)

        lidar_xyz = lidar_pc.points[:3, :]
        points_camera = transform_points(
            lidar_xyz,
            T_camera_lidar
        )
        print("\nLiDAR points:", lidar_xyz.shape[1])
        print("Points in camera frame:", points_camera.shape)

        pixels, front_mask = project_to_image(
            points_camera,
            camera_calib.intrinsic
        )
        print("Points in front of camera:", pixels.shape[1])


        # filter boundary
        image = Image.open(cam_path)
        width, height = image.size
        u = pixels[0, :]
        v = pixels[1, :]
        image_mask = (
            (u >= 0) &
            (u < width) &
            (v >= 0) &
            (v < height)
        )
        pixels_visible = pixels[:, image_mask]
        print("Points inside image:", pixels_visible.shape[1])

        # depth test
        depth_front = points_camera[2, front_mask]
        depth_visible = depth_front[image_mask]

        plt.figure(figsize=(14, 8))
        plt.imshow(image)

        scatter=plt.scatter(
            pixels_visible[0, :],
            pixels_visible[1, :],
            c=depth_visible,
            s=3,
            cmap='turbo'
        )

        cbar = plt.colorbar(scatter)
        cbar.set_label("Depth [m]")

        plt.title("LiDAR Projection on CAM_FRONT - depth colored")
        plt.axis("off")

        plt.savefig(
            f"outputs/v2/frame_{frame_idx:04d}.png",
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()

        frame_idx += 1

        sample_token = sample["next"]




if __name__ == "__main__":
    main()