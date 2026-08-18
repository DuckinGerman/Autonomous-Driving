import matplotlib.pyplot as plt
from nuscenes.nuscenes import NuScenes
from nuscenes.utils.data_classes import LidarPointCloud

from src.bev.rasterizer import BEVRasterizer
import numpy as np

def main():
    nusc = NuScenes(
        version="v1.0-mini",
        dataroot="datasets/nuscenes",
        verbose=False
    )

    sample = nusc.sample[0]

    lidar_token = sample["data"]["LIDAR_TOP"]
    lidar_path = nusc.get_sample_data_path(lidar_token)

    lidar_pc = LidarPointCloud.from_file(lidar_path)

    rasterizer = BEVRasterizer()

    # lidar point 2 bev 70,50
    rows, cols, valid_mask = rasterizer.points_to_grid(
        lidar_pc.points
    )

    print("Original LiDAR points:", lidar_pc.points.shape[1])
    print("Points inside BEV ROI:", valid_mask.sum())
    print("BEV shape:", rasterizer.height, rasterizer.width)

    plt.figure(figsize=(8, 10))
    plt.scatter(
        cols,
        rows,
        s=0.5
    )

    plt.xlim(0, rasterizer.width)
    plt.ylim(rasterizer.height, 0)
    plt.title("LiDAR Points in BEV Grid Coordinates")
    plt.xlabel("BEV column")
    plt.ylabel("BEV row")

    plt.savefig(
        "outputs/v3/bev_grid_test.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    # height map
    height_map = rasterizer.create_height_map(
        lidar_pc.points
    )

    print("Height map shape:", height_map.shape)
    print("Minimum height:", height_map.min())
    print("Maximum height:", height_map.max())

    plt.figure(figsize=(8, 10))

    plt.imshow(
        height_map,
        cmap="viridis"
    )

    plt.colorbar(label="Height [m]")
    plt.title("LiDAR BEV Height Map")
    plt.xlabel("BEV column")
    plt.ylabel("BEV row")

    plt.savefig(
        "outputs/v3/bev_height_map.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    # density map
    density_map = rasterizer.create_density_map(
        lidar_pc.points
    )

    print("Density map shape:", density_map.shape)
    print("Density min:", density_map.min())
    print("Density max:", density_map.max())

    plt.figure(figsize=(8, 10))

    plt.imshow(
        density_map,
        cmap="gray"
    )

    plt.colorbar(label="Normalized Point Density")
    plt.title("LiDAR BEV Density Map")
    plt.xlabel("BEV column")
    plt.ylabel("BEV row")

    plt.savefig(
        "outputs/v3/bev_density_map.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()


    # intensity map
    intensity_map = rasterizer.create_intensity_map(
        lidar_pc.points
    )

    print("Intensity map shape:", intensity_map.shape)
    print("Intensity min:", intensity_map.min())
    print("Intensity max:", intensity_map.max())

    plt.figure(figsize=(8, 10))

    plt.imshow(
        intensity_map,
        cmap="gray"
    )

    plt.colorbar(label="Normalized Intensity")
    plt.title("LiDAR BEV Intensity Map")
    plt.xlabel("BEV column")
    plt.ylabel("BEV row")

    plt.savefig(
        "outputs/v3/bev_intensity_map.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    # all 3 fusion as tensor npy
    bev_tensor = np.stack([
        height_map,
        density_map,
        intensity_map
    ], axis=0)

    print("BEV tensor:", bev_tensor.shape)
    print("Min:", bev_tensor.min())
    print("Max:", bev_tensor.max())

    np.save('outputs/v3/bev_tensor.npy', bev_tensor)


    # rgb-like bev
    bev_rgb = np.stack([
        height_map,
        density_map,
        intensity_map
    ], axis=-1)


    plt.figure(figsize=(8, 10))

    plt.imshow(bev_rgb)

    plt.title(
        "LiDAR BEV Representation\n"
        "R: Height | G: Density | B: Intensity"
    )

    plt.xlabel("BEV column")
    plt.ylabel("BEV row")

    plt.savefig(
        "outputs/v3/bev_rgb.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()


if __name__ == "__main__":
    main()