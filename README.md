# V1 - nuScenes Dataset Explorer

## Overview

The goal of V1 is **not** to build a perception model, but to understand the data organization of a modern autonomous driving dataset.

This project explores the nuScenes mini dataset by parsing the complete data pipeline from raw sensor data to vehicle poses.

The implemented pipeline is:

```
Scene
    ↓
Sample
    ↓
Sample Data
    ├── Camera
    ├── LiDAR
    └── Radar
    ↓
Calibrated Sensor
    ↓
Ego Pose
```

---

## Dataset

- Dataset: nuScenes v1.0-mini
- Number of scenes: **10**
- Number of samples: **404**
- Sensors:
  - 6 Cameras
  - 1 LiDAR
  - 5 Radars

---

## Project Structure

```
Autonomous-Driving-AI
│
├── datasets/
├── outputs/
│   └── v1/
│       ├── cam_front.png
│       └── lidar_bev.png
│
├── scripts/
│   └── explore_dataset.py
│
└── src/
```

---

# What has been implemented

## 1. Camera

The first front-view camera image was successfully loaded and visualized.

Output:

```
CAM_FRONT
↓
JPEG Image
```

Result:

`outputs/v1/cam_front.png`

---

## 2. LiDAR

The LiDAR point cloud was loaded.

```
Point Cloud Shape

(4, N)

x
y
z
intensity
```

The x-y coordinates were projected into Bird's Eye View (BEV).

Result:

`outputs/v1/lidar_bev.png`

---

## 3. Radar

Radar data was successfully parsed.

```
Radar Shape

(18, 74)
```

Meaning:

- 74 radar detections
- Each detection contains 18 attributes
- Radar additionally provides motion-related information such as velocity.

---

## 4. Camera Calibration

Camera calibration parameters were extracted.

### Translation

```
[1.70, 0.02, 1.51]
```

Meaning:

The camera is mounted

- 1.70 m in front of the ego vehicle
- 0.02 m to the left/right
- 1.51 m above the ground

---

### Rotation

Quaternion describing the camera orientation relative to the ego vehicle.

---

### Camera Intrinsic

```
fx  0  cx
0  fy  cy
0   0   1
```

Meaning:

The intrinsic matrix projects 3D camera coordinates into image pixels.

---

## 5. Ego Pose

Vehicle pose in the global map.

Example:

```
Translation

[411.42,
1181.20,
0.00]
```

Meaning:

The ego vehicle is located at this position in the global coordinate system.

---

# Coordinate Frames

```
Camera Frame
        │
        ▼
Calibrated Sensor
        │
        ▼
Ego Vehicle Frame
        │
        ▼
Global Frame
```

This coordinate hierarchy is the geometric foundation for 3D perception algorithms.

---

# V1 Summary

In this version, no deep learning model is used.

The objective is to understand

- dataset organization
- sensor modalities
- calibration
- coordinate systems
- ego poses

These components serve as the basis for future versions involving

- Camera-LiDAR projection
- Sensor Fusion
- BEV perception
- Trajectory prediction

---

# Next Version

**V2 – Camera-LiDAR Geometry**

Goals:

- Parse LiDAR calibration
- Transform LiDAR points into the ego frame
- Transform ego frame into camera frame
- Project LiDAR points onto the camera image