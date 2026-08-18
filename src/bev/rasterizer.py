"""
1.
真实世界坐标 (x, y)
        ↓
BEV 像素坐标 (row, col)
LiDAR point:
x = 10 m
y = 2 m

        ↓

BEV grid:
row = ...
col = ...
2.
对每一个 BEV 网格，记录落在这个格子里的 LiDAR 点的最大 z 值
很多 3D 点
    ↓
落到同一个 BEV cell
    ↓
取最高点
    ↓
形成高度图
3.
Height Map
→ 这个位置最高的物体有多高

Density Map 
→ 这个位置的 LiDAR 点有多密

intensity map qiangdu tu 
4. fusion
"""
import numpy as np


class BEVRasterizer:
    def __init__(
        self,
        x_range=(-20.0, 50.0),
        y_range=(-25.0, 25.0),
        resolution=0.1,
    ):
        self.x_range = x_range
        self.y_range = y_range
        self.resolution = resolution

        self.height = int(
            (x_range[1] - x_range[0]) / resolution
        )

        self.width = int(
            (y_range[1] - y_range[0]) / resolution
        )

    def points_to_grid(self, points):
        """
        Convert LiDAR XY coordinates to BEV grid indices.

        Args:
            points: numpy array with shape (3, N) or (4, N)

        Returns:
            row_indices
            col_indices
            valid_mask
        """

        x = points[0, :]
        y = points[1, :]

        valid_mask = (
            (x >= self.x_range[0])
            & (x < self.x_range[1])
            & (y >= self.y_range[0])
            & (y < self.y_range[1])
        )

        x_valid = x[valid_mask]
        y_valid = y[valid_mask]

        rows = (
            (self.x_range[1] - x_valid)
            / self.resolution
        ).astype(np.int32)

        cols = (
            (y_valid - self.y_range[0])
            / self.resolution
        ).astype(np.int32)

        return rows, cols, valid_mask

    def create_height_map(self, points):
        """
        Create a BEV height map from LiDAR points.

        Args:
            points: numpy array with shape (4, N)

        Returns:
            height_map: (H, W)
        """

        rows, cols, valid_mask = self.points_to_grid(points)

        z = points[2, valid_mask]

        height_map = np.full(
            (self.height, self.width),
            -np.inf,
            dtype=np.float32
        )

        for r, c, height in zip(rows, cols, z):
            if height > height_map[r, c]:
                height_map[r, c] = height

        height_map[height_map == -np.inf] = 0.0

        # 现在的 density 和 intensity 都已经接近 [0,1]，但 height_map 还是米，所以三个 channel 的数值尺度不一致。
        # Clip extreme heights.
        height_map = np.clip(height_map, -2.0, 3.0)

        # Normalize to [0, 1].
        height_map = (height_map + 2.0) / 5.0

        return height_map

    def create_density_map(self, points):
        """
        Create a BEV density map from LiDAR points.
        每一个 BEV cell 里落了多少个 LiDAR 点。

        Args:
            points: numpy array with shape (4, N)

        Returns:
            density_map: (H, W)
        """

        rows, cols, valid_mask = self.points_to_grid(points)

        density_map = np.zeros(
            (self.height, self.width),
            dtype=np.float32
        )

        for r, c in zip(rows, cols):
            density_map[r, c] += 1.0

        # Log normalization to reduce the effect of very dense cells.
        density_map = np.log1p(density_map)

        if density_map.max() > 0:
            density_map /= density_map.max()

        return density_map

    def create_intensity_map(self, points):
        """
        Create a BEV intensity map from LiDAR points.

        Args:
            points: numpy array with shape (4, N)

        Returns:
            intensity_map: (H, W)
        """

        rows, cols, valid_mask = self.points_to_grid(points)

        intensity = points[3, valid_mask]

        intensity_map = np.zeros(
            (self.height, self.width),
            dtype=np.float32
        )

        count_map = np.zeros(
            (self.height, self.width),
            dtype=np.float32
        )

        for r, c, value in zip(rows, cols, intensity):
            intensity_map[r, c] += value
            count_map[r, c] += 1.0

        valid_cells = count_map > 0
        intensity_map[valid_cells] /= count_map[valid_cells]

        if intensity_map.max() > 0:
            intensity_map /= intensity_map.max()

        return intensity_map

    